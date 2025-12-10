import requests
from typing import Dict, Any
from core.config import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"

def initialize_transaction(email: str, amount: int, reference: str) -> Dict[str, Any]:
    """
    Initializes a Paystack transaction.
    Amount is in the smallest currency unit (e.g., kobo for Naira).
    """
    if settings.PAYSTACK_SECRET_KEY.startswith("sk_test_mock"):
        return {
            "status": True,
            "data": {"authorization_url": f"https://paystack.co/checkout/{reference}"}
        }
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": amount,
        "reference": reference,
        "callback_url": f"{settings.BASE_URL}/wallet/deposit/callback"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Log the error appropriately
        print(f"Error initializing Paystack transaction: {e}")
        return {"status": False, "message": str(e)}
    
def verify_transaction(reference: str) -> Dict[str, Any]:
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Paystack verification failed: {e}")
        return {"status": False, "message": str(e)}
