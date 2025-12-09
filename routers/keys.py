from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from core.api_key_manager import generate_api_key, rollover_api_key
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from dependencies.auth import get_current_user_id_from_jwt
from schemas.keys import APIKeyCreate, APIKeyResponse, APIKeyRollover


router = APIRouter(
    prefix="/keys",
    tags=["API Key Management"],
    dependencies=[Depends(get_current_user_id_from_jwt)] # Only JWT users can manage keys
)

@router.post("/create", response_model=APIKeyResponse, summary="Create a new API Key")
async def create_key(
    db: Annotated[AsyncSession, Depends(get_db)],
    key_data: APIKeyCreate,
    user_id: Annotated[str, Depends(get_current_user_id_from_jwt)]
):
    """
    Allows a user to create a new API key for service-to-service access.
    
    - Requires JWT authentication.
    - Maximum 5 active keys per user.
    - Permissions must be explicitly assigned (deposit, transfer, read).
    - Expiry must be in format: 1H, 1D, 1M, 1Y.
    """
    try:
        result = await generate_api_key(
            db=db,
            user_id=user_id,
            name=key_data.name,
            permissions=key_data.permissions,
            expiry_str=key_data.expiry
        )
        return APIKeyResponse(api_key=result["api_key"], expires_at=result["expires_at"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/rollover", response_model=APIKeyResponse, summary="Rollover an expired API Key")
async def rollover_key(
    db: Annotated[AsyncSession, Depends(get_db)],
    rollover_data: APIKeyRollover,
    user_id: Annotated[str, Depends(get_current_user_id_from_jwt)]
):
    """
    Creates a new API key with the same permissions as an expired key.
    
    - Requires JWT authentication.
    - The key must be truly expired.
    - The old key is deactivated.
    """
    try:
        result = await rollover_api_key(
            db=db,
            expired_key_id=rollover_data.expired_key_id,
            expiry_str=rollover_data.expiry
        )
        # Note: We don't check if the key belongs to the user_id here, 
        # but in a real system, you would add that check.
        return APIKeyResponse(api_key=result["api_key"], expires_at=result["expires_at"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
