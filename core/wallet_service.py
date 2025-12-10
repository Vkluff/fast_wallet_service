import uuid
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.models import User, Wallet, Transaction
from core.paystack_client import initialize_transaction
from schemas.wallet import DepositResponse


# --- Helper Functions for DB Access ---

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, email: str, name: str) -> User:
    # 1. Create User
    # Since this is a mock Google login, we set a short, safe placeholder password
    new_user = User(email=email, name=name)
    db.add(new_user)
    await db.flush() # Flush to get the user ID

    # 2. Create Wallet for User
    wallet_number = str(uuid.uuid4()).replace("-", "")[:15]
    new_wallet = Wallet(user_id=new_user.id, wallet_number=wallet_number, balance=0)
    db.add(new_wallet)
    
    # We don't commit here, as the calling function (auth router) will commit
    return new_user

async def get_wallet_by_user_id(db: AsyncSession, user_id: str) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_wallet_by_wallet_number(db: AsyncSession, wallet_number: str) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.wallet_number == wallet_number)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_transaction_by_reference(db: AsyncSession, reference: str) -> Transaction | None:
    stmt = select(Transaction).where(Transaction.reference == reference)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# --- Wallet Service Logic ---

async def initiate_deposit(db: AsyncSession, user_id: str, amount: int, email: str) -> DepositResponse:
    """
    Initializes a deposit transaction with Paystack.
    """
    wallet = await get_wallet_by_user_id(db, user_id)
    if not wallet:
        raise ValueError("Wallet not found for user.")
        
    # 1. Generate unique reference
    reference = f"DEP-{uuid.uuid4().hex[:10]}-{user_id[:4]}"
    
    # 2. Record transaction as pending
    new_transaction = Transaction(
        wallet_id=wallet.id,
        type="deposit",
        amount=amount,
        status="pending",
        reference=reference,
        meta={"email": email, "user_id": user_id} # Store user_id for webhook lookup
    )
    db.add(new_transaction)
    await db.flush() # Ensure transaction is in DB before calling Paystack
    
    # 3. Call Paystack to initialize
    paystack_response = initialize_transaction(email=email, amount=amount, reference=reference)
    
    if not paystack_response.get("status"):
        # If Paystack fails, update transaction status to failed
        new_transaction.status = "failed"
        raise ConnectionError(f"Paystack initialization failed: {paystack_response.get('message', 'Unknown error')}")
        
    return DepositResponse(
        reference=reference,
        authorization_url=paystack_response["data"]["authorization_url"]
    )

async def handle_paystack_webhook(db: AsyncSession, payload: Dict[str, Any]) -> bool:
    """
    Handles Paystack webhook – credits wallet only on success.
    Fully idempotent and atomic.
    """
    event = payload.get("event")
    if event != "charge.success":
        return False

    data = payload.get("data", {})
    reference = data.get("reference")
    amount_kobo = data.get("amount", 0)

    if not reference:
        return False

    # Find our pending transaction
    transaction = await get_transaction_by_reference(db, reference)
    if not transaction:
        # This is a critical error, log and alert
        return False

    # Idempotency – already credited?
    if transaction.status == "success":
        return True

    if transaction.status == "pending":
        user_id = transaction.meta.get("user_id")
        if not user_id:
            # Critical error: user_id missing from meta
            return False

        wallet = await get_wallet_by_user_id(db, user_id)
        if not wallet:
            # Critical error: wallet not found
            return False

        # Convert kobo → your currency (e.g., Naira)
        # Note: Paystack amount is in the smallest currency unit (e.g., kobo).
        # We assume the 'amount' stored in our transaction is also in the smallest unit.
        # For simplicity, we use the amount from the webhook data.
        
        # 1. Credit wallet
        wallet.balance += amount_kobo
        
        # 2. Update transaction status
        transaction.status = "success"
        
        # The session commit in get_db dependency will save changes
        return True

    return False

async def get_wallet_balance(db: AsyncSession, user_id: str) -> int:
    """Retrieves the current wallet balance for a user."""
    wallet = await get_wallet_by_user_id(db, user_id)
    if not wallet:
        raise ValueError("Wallet not found for user.")
    return wallet.balance



async def get_transaction_history(db: AsyncSession, user_id: str) -> List[Transaction]:
    """Retrieves the transaction history for a user."""
    wallet = await get_wallet_by_user_id(db, user_id)
    if not wallet:
        raise ValueError("Wallet not found for user.")
    
    # Load transactions associated with the wallet
    stmt = select(Transaction).where(Transaction.wallet_id == wallet.id).order_by(Transaction.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def transfer_funds(db: AsyncSession, sender_user_id: str, recipient_wallet_number: str, amount: int) -> bool:
    """
    Performs an atomic wallet-to-wallet transfer.
    """
    sender_wallet = await get_wallet_by_user_id(db, sender_user_id)
    recipient_wallet = await get_wallet_by_wallet_number(db, recipient_wallet_number)
    
    if not sender_wallet:
        raise ValueError("Sender wallet not found.")
    if not recipient_wallet:
        raise ValueError("Recipient wallet not found.")
        
    if sender_wallet.user_id == recipient_wallet.user_id:
        raise ValueError("Cannot transfer funds to your own wallet.")

    if sender_wallet.balance < amount:
        raise ValueError("Insufficient balance for transfer.")
        
    # --- Atomic Transfer ---
    
    # 1. Debit sender
    sender_wallet.balance -= amount
    
    sender_transaction = Transaction(
        wallet_id=sender_wallet.id,
        type="transfer_out",
        amount=amount,
        status="success",
        reference=f"TRF-{uuid.uuid4().hex[:10]}-{sender_user_id[:4]}",
        meta={"recipient_wallet_number": recipient_wallet_number, "recipient_user_id": recipient_wallet.user_id}
    )
    db.add(sender_transaction)
    
    # 2. Credit recipient
    recipient_wallet.balance += amount
    
    recipient_transaction = Transaction(
        wallet_id=recipient_wallet.id,
        type="transfer_in",
        amount=amount,
        status="success",
        reference=f"TRF-{uuid.uuid4().hex[:10]}-{recipient_wallet.user_id[:4]}",
        meta={"sender_user_id": sender_user_id, "sender_wallet_number": sender_wallet.wallet_number}
    )
    db.add(recipient_transaction)
    
    # The session commit in get_db dependency will save all changes atomically
    return True

async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()