from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_db
from core.security import create_access_token
from core.wallet_service import create_user, get_user_by_email
from schemas.auth import Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# --- Mock Google Sign-in ---
# In a real application, this would redirect to Google's OAuth server.
@router.get("/google", summary="Initiate Google Sign-in (Mocked)")
async def google_login():
    """
    **MOCK ENDPOINT**

    In a real application, this would redirect the user to Google's OAuth consent screen.

    For this tutorial, we will simulate the redirect to the callback with a mock user email.
    """
    # Simulate a successful redirect from Google with a code
    mock_email = "test.user@example.com"
    return RedirectResponse(
        url=f"{settings.BASE_URL}/auth/google/callback?email={mock_email}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/google/callback", response_model=Token, summary="Google Sign-in Callback (Mocked)"
)
async def google_callback(email: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    **MOCK ENDPOINT**

    In a real application, this would exchange the authorization code for user info.

    Here, we use the mock `email` query parameter to simulate a successful login.
    """

    # 1. Find or Create User
    user = await get_user_by_email(db, email)
    if not user:
        # Simulate creating a new user on first login
        user = await create_user(db, email=email, name=email.split("@")[0].capitalize())

    # 2. Create JWT Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token)
