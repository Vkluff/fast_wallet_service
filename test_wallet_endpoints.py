import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timedelta

from main import app
from core.db import Base, get_db
from core.config import settings
from core.models import User, Wallet, Transaction, APIKey
from core.security import create_access_token

# Test database URL - use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Client fixture
@pytest.fixture(scope="function")
async def client():
    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Override the get_db dependency
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Clear overrides
    app.dependency_overrides.clear()

# Test user data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"

# Fixture to create a test user and wallet
@pytest.fixture(scope="function")
async def test_user():
    async with TestingSessionLocal() as session:
        # Create a test user
        user = User(
            email=TEST_USER_EMAIL,
            hashed_password=TEST_USER_PASSWORD,  # In a real test, this should be hashed
            name="Test User"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Create a wallet for the user
        wallet = Wallet(
            user_id=user.id,
            wallet_number="1234567890",
            balance=1000  # Starting balance of 10.00 (assuming smallest unit is 0.01)
        )
        session.add(wallet)
        await session.commit()
        
        # Create an API key for the user
        api_key = APIKey(
            user_id=user.id,
            key_hash="testapikey123",
            name="Test API Key",
            permissions=["deposit", "transfer", "read"],
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        session.add(api_key)
        await session.commit()
        
        return user, wallet, api_key

# Test JWT token generation
def get_test_token(user_id: str):
    access_token_expires = timedelta(minutes=30)
    return create_access_token(
        data={"sub": user_id, "email": TEST_USER_EMAIL},
        expires_delta=access_token_expires
    )

# Test deposit endpoint
@pytest.mark.asyncio
async def test_deposit_endpoint(client, test_user):
    user, wallet, api_key = test_user
    
    # Get JWT token
    token = get_test_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test deposit with valid amount
    deposit_data = {"amount": 5000}  # 50.00 in smallest unit
    response = client.post("/wallet/deposit", json=deposit_data, headers=headers)
    
    assert response.status_code == 200
    assert "reference" in response.json()
    assert "authorization_url" in response.json()
    
    # Test deposit with invalid amount
    invalid_deposit_data = {"amount": -100}  # Negative amount
    response = client.post("/wallet/deposit", json=invalid_deposit_data, headers=headers)
    assert response.status_code == 400

# Test deposit status endpoint
@pytest.mark.asyncio
async def test_deposit_status_endpoint(client, test_user):
    user, wallet, api_key = test_user
    
    # Create a test transaction
    async with TestingSessionLocal() as session:
        transaction = Transaction(
            wallet_id=wallet.id,
            type="deposit",
            amount=5000,
            status="pending",
            reference="TEST123",
            meta={"email": TEST_USER_EMAIL, "user_id": str(user.id)}
        )
        session.add(transaction)
        await session.commit()
    
    # Test checking deposit status
    response = client.get(f"/wallet/deposit/TEST123/status")
    assert response.status_code == 200
    assert response.json()["reference"] == "TEST123"
    assert response.json()["status"] == "pending"
    assert response.json()["amount"] == 5000

# Test transfer endpoint
@pytest.mark.asyncio
async def test_transfer_endpoint(client, test_user):
    user, wallet, api_key = test_user
    
    # Create a recipient user and wallet
    async with TestingSessionLocal() as session:
        recipient = User(
            email="recipient@example.com",
            hashed_password="recipientpass",
            name="Recipient User"
        )
        session.add(recipient)
        await session.commit()
        
        recipient_wallet = Wallet(
            user_id=recipient.id,
            wallet_number="0987654321",
            balance=500  # 5.00 in smallest unit
        )
        session.add(recipient_wallet)
        await session.commit()
    
    # Get JWT token
    token = get_test_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test transfer with valid amount
    transfer_data = {
        "wallet_number": "0987654321",
        "amount": 300  # 3.00 in smallest unit
    }
    response = client.post("/wallet/transfer", json=transfer_data, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify balances
    async with TestingSessionLocal() as session:
        # Refresh sender wallet
        sender_wallet = await session.get(Wallet, wallet.id)
        assert sender_wallet.balance == 1000 - 300  # 700
        
        # Refresh recipient wallet
        updated_recipient_wallet = await session.get(Wallet, recipient_wallet.id)
        assert updated_recipient_wallet.balance == 500 + 300  # 800

# Test wallet balance endpoint
@pytest.mark.asyncio
async def test_wallet_balance_endpoint(client, test_user):
    user, wallet, api_key = test_user
    
    # Get JWT token
    token = get_test_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting wallet balance
    response = client.get("/wallet/balance", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["balance"] == wallet.balance
    assert response.json()["wallet_number"] == wallet.wallet_number

# Test transactions history endpoint
@pytest.mark.asyncio
async def test_transactions_history_endpoint(client, test_user):
    user, wallet, api_key = test_user
    
    # Create some test transactions
    async with TestingSessionLocal() as session:
        transactions = [
            Transaction(
                wallet_id=wallet.id,
                type="deposit",
                amount=1000,
                status="success",
                reference=f"DEP-{i}",
                meta={"email": TEST_USER_EMAIL, "user_id": str(user.id)}
            ) for i in range(3)
        ]
        session.add_all(transactions)
        await session.commit()
    
    # Get JWT token
    token = get_test_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting transaction history
    response = client.get("/wallet/transactions", headers=headers)
    
    assert response.status_code == 200
    assert len(response.json()) == 3  # Should have 3 transactions
    assert all(tx["type"] == "deposit" for tx in response.json())
    assert all(tx["status"] == "success" for tx in response.json())

# Test API key authentication
@pytest.mark.asyncio
async def test_api_key_authentication(client, test_user):
    user, wallet, api_key = test_user
    
    # Test with API key in header
    headers = {"x-api-key": "testapikey123"}
    
    # Test getting wallet balance with API key
    response = client.get("/wallet/balance", headers=headers)
    assert response.status_code == 200
    assert response.json()["wallet_number"] == wallet.wallet_number
