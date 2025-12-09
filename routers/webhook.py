from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import hmac
import hashlib

from core.db import get_db
from core.wallet_service import handle_paystack_webhook
from core.config import settings
from schemas.common import MessageResponse
router = APIRouter(
    tags=["Webhooks"],
)

@router.post("/wallet/paystack/webhook", response_model=MessageResponse, summary="Paystack Webhook Handler (Mandatory)")
async def paystack_webhook_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Receives and validates Paystack webhooks. This is the ONLY place that should credit the user's wallet.
    """
    # 1. Get raw body (required for signature)
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature")

    # 2. CRITICAL: Verify it's really from Paystack
    # Note: We use PAYSTACK_SECRET_KEY for webhook verification
    expected_signature = hmac.new(
        settings.PAYSTACK_WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature or ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Paystack signature")

    # 3. Safe to process
    try:
        event_data = await request.json()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    if await handle_paystack_webhook(db, event_data):
        return MessageResponse(message="Webhook processed successfully.")
    else:
        return MessageResponse(message="Webhook received, but no action was taken (e.g., not a success event or already processed).")
