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

class Transaction(ORMBase):
    type: str = Field(..., description="Transaction type: deposit|transfer_out|transfer_in")
    amount: int
    status: str = Field(..., description="Transaction status: success|failed|pending")

class TransactionHistoryResponse(RootModel[List[Transaction]]):
    pass
