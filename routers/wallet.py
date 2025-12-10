from fastapi import Depends, requests, status, HTTPException, APIRouter, Header
from typing import List, Dict, Any, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from core.wallet_service import (
    get_user_by_email, get_transaction_by_reference,
    initiate_deposit, handle_paystack_webhook,
    get_wallet_balance, get_transaction_history,
    transfer_funds, get_user_by_id, get_wallet_by_user_id
)

from dependencies.auth import (
    get_user_id_for_deposit, get_user_id_for_read, 
    get_user_id_for_transfer)

from schemas.wallet import (
    DepositRequest, DepositResponse, DepositStatusResponse, 
    TransferRequest, TransferResponse, Transaction
)

from core.db import get_db

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet Operations"],
)

@router.post("/deposit", response_model=DepositResponse, summary="Initiate a wallet deposit via Paystack")
async def deposit(
    db: Annotated[AsyncSession, Depends(get_db)],
    deposit_data: DepositRequest,
    user_id: Annotated[str, Depends(get_user_id_for_deposit)]
):
    """
    Initiates a deposit transaction. Requires JWT or API Key with 'deposit' permission.
    Returns a Paystack authorization URL for the user to complete the payment.
    """
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
            
        return await initiate_deposit(
            db=db,
            user_id=user_id, 
            amount=deposit_data.amount, 
            email=user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))



@router.get("/deposit/{reference}/status", response_model=DepositStatusResponse, summary="Verify deposit status (Manual Check)")
async def get_deposit_status(
    reference: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Manually check the status of a deposit transaction. This endpoint does NOT credit the wallet.
    """
    transaction = await get_transaction_by_reference(db, reference)
    
    if not transaction or transaction.type != "deposit":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deposit transaction not found.")
        
    # In a real app, you would call Paystack's verify endpoint here as a fallback
    # For this mock, we return the status from our DB
    return DepositStatusResponse(
        reference=reference,
        status=transaction.status,
        amount=transaction.amount
    )

@router.post("/transfer", response_model=TransferResponse, summary="Transfer funds to another user's wallet")
async def transfer(
    db: Annotated[AsyncSession, Depends(get_db)],
    transfer_data: TransferRequest,
    user_id: Annotated[str, Depends(get_user_id_for_transfer)]
):
    """
    Transfers funds from the authenticated user's wallet to another user's wallet.
    Requires JWT or API Key with 'transfer' permission.
    """
    try:
        await transfer_funds(
            db=db,
            sender_user_id=user_id,
            recipient_wallet_number=transfer_data.wallet_number,
            amount=transfer_data.amount
        )
        return TransferResponse(status="success", message="Transfer completed successfully.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/balance", summary="Get current wallet balance")
async def balance(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[str, Depends(get_user_id_for_read)]
):
    """
    Retrieves the current balance of the authenticated user's wallet.
    Requires JWT or API Key with 'read' permission.
    """
    try:
        wallet = await get_wallet_by_user_id(db, user_id)
        if not wallet:
            raise ValueError("Wallet not found for user.")
        return {"balance": wallet.balance, "wallet_number": wallet.wallet_number}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/transactions", response_model=List[Transaction], summary="Get transaction history")
async def transactions(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[str, Depends(get_user_id_for_read)]
):
    """
    Retrieves the transaction history for the authenticated user's wallet.
    Requires JWT or API Key with 'read' permission.
    """
    try:
        history = await get_transaction_history(db, user_id)
        # Convert ORM models to Pydantic models
        return [Transaction.model_validate(t) for t in history]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
