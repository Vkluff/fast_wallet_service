from pydantic import BaseModel, Field, RootModel
from schemas.common import ORMBase
from typing import List

class DepositRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to deposit in the smallest currency unit (e.g., kobo for Naira).")

class DepositResponse(BaseModel):
    reference: str = Field(..., description="Unique transaction reference.")
    authorization_url: str = Field(..., description="Paystack payment link.")

class PaystackWebhookData(BaseModel):
    """Simplified model for Paystack webhook data (event type and transaction reference are key)."""
    event: str
    data: dict

class DepositStatusResponse(BaseModel):
    reference: str
    status: str = Field(..., description="Transaction status: success|failed|pending")
    amount: int

class TransferRequest(BaseModel):
    wallet_number: str = Field(..., description="Recipient's wallet number.")
    amount: int = Field(..., gt=0, description="Amount to transfer in the smallest currency unit.")

class TransferResponse(BaseModel):
    status: str = Field(..., description="Transfer status: success|failed")
    message: str

class TransactionMeta(BaseModel):
    """Schema for transaction metadata."""
    email: str | None = Field(None, description="Email associated with the transaction")
    user_id: str | None = Field(None, description="User ID associated with the transaction")
    recipient_wallet_number: str | None = Field(None, description="Recipient's wallet number for transfers")
    recipient_user_id: str | None = Field(None, description="Recipient's user ID for transfers")
    sender_user_id: str | None = Field(None, description="Sender's user ID for transfers")
    sender_wallet_number: str | None = Field(None, description="Sender's wallet number for transfers")

class Transaction(ORMBase):
    """Transaction model for API responses."""
    type: str = Field(..., description="Transaction type: deposit|transfer_out|transfer_in")
    amount: int = Field(..., description="Transaction amount in the smallest currency unit")
    status: str = Field(..., description="Transaction status: success|failed|pending")
    reference: str = Field(..., description="Unique transaction reference")
    meta: TransactionMeta = Field(default_factory=dict, description="Additional transaction metadata")

class TransactionHistoryResponse(RootModel[List[Transaction]]):
    pass
