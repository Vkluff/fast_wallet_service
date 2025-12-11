import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from core.db import Base, get_db
from core.models import User, Wallet, Transaction, APIKey
from core.security import create_access_token

# Test database URL - use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Test user data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"

async def setup_database():
    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a test user and wallet
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
        data={"sub": str(user_id), "email": TEST_USER_EMAIL},
        expires_delta=access_token_expires
    )

async def run_tests():
    # Set up the database and get test data
    user, wallet, api_key = await setup_database()
    
    # Override the get_db dependency
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    
    print("\n=== Testing Wallet Endpoints ===\n")
    
    # Test 1: Get JWT token
    print("1. Testing JWT token generation...")
    token = get_test_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   - Token: {token[:20]}...")
    
    # Test 2: Get wallet balance
    print("\n2. Testing wallet balance endpoint...")
    response = client.get("/wallet/balance", headers=headers)
    print(f"   - Status Code: {response.status_code}")
    print(f"   - Response: {response.json()}")
    
    # Test 3: Test deposit endpoint
    print("\n3. Testing deposit endpoint...")
    deposit_data = {"amount": 5000}  # 50.00 in smallest unit
    response = client.post("/wallet/deposit", json=deposit_data, headers=headers)
    print(f"   - Status Code: {response.status_code}")
    print(f"   - Response: {response.json()}")
    
    # Extract reference from deposit response
    reference = response.json().get("reference")
    
    # Test 4: Test deposit status endpoint
    if reference:
        print(f"\n4. Testing deposit status for reference: {reference}")
        response = client.get(f"/wallet/deposit/{reference}/status")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Response: {response.json()}")
    
    # Test 5: Test transfer endpoint
    print("\n5. Testing transfer endpoint...")
    # First, create a recipient user and wallet
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
        
        # Test transfer with valid amount
        transfer_data = {
            "wallet_number": "0987654321",
            "amount": 300  # 3.00 in smallest unit
        }
        response = client.post("/wallet/transfer", json=transfer_data, headers=headers)
        print(f"   - Transfer Status Code: {response.status_code}")
        print(f"   - Transfer Response: {response.json()}")
        
        # Verify balances after transfer
        sender_wallet = await session.get(Wallet, wallet.id)
        updated_recipient_wallet = await session.get(Wallet, recipient_wallet.id)
        print(f"   - Sender's new balance: {sender_wallet.balance}")
        print(f"   - Recipient's new balance: {updated_recipient_wallet.balance}")
    
    # Test 6: Test transactions history endpoint
    print("\n6. Testing transactions history endpoint...")
    response = client.get("/wallet/transactions", headers=headers)
    print(f"   - Status Code: {response.status_code}")
    transactions = response.json()
    print(f"   - Number of transactions: {len(transactions)}")
    if transactions:
        print(f"   - First transaction: {transactions[0]}")
    
    # Test 7: Test API key authentication
    print("\n7. Testing API key authentication...")
    api_key_headers = {"x-api-key": "testapikey123"}
    response = client.get("/wallet/balance", headers=api_key_headers)
    print(f"   - Status Code with API Key: {response.status_code}")
    print(f"   - Balance with API Key: {response.json()}")
    
    # Clean up
    print("\n=== Test Complete ===\n")
    
    # Clear overrides
    app.dependency_overrides.clear()
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

if __name__ == "__main__":
    asyncio.run(run_tests())
