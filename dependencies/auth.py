from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
from typing import Annotated, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import decode_access_token
from core.wallet_service import get_user_by_email
from core.api_key_manager import get_api_key_data
from core.db import get_db
from core.models import APIKey
from schemas.auth import TokenData
from schemas.keys import APIKeyPermissions

bearer_scheme = HTTPBearer(auto_error=False)

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def get_current_user_id_from_jwt(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]  # ← CHANGED: use bearer_scheme + credentials
) -> str | None:
    """
    Dependency to get the current user ID from a JWT token.
    Raises 401 if token is invalid or expired.
    """
    if credentials is None:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    token_data: TokenData = decode_access_token(token)
    
    if token_data is None:
        raise credentials_exception
        
    user = await get_user_by_email(db, token_data.email)
    
    if user is None:
        raise credentials_exception
        
    return user.id

async def get_current_api_key_data(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_api_key: Annotated[str | None, Depends(api_key_header)] = None  # ← CHANGED: use api_key_header
) -> APIKey | None:
    """
    Dependency to get the API key data from the x-api-key header.
    Returns None if header is missing or key is invalid.
    """
    if x_api_key:
        key_data = await get_api_key_data(db, x_api_key)
        if key_data:
            return key_data
    return None

async def get_current_user_id(
    jwt_user_id: Annotated[str | None, Depends(get_current_user_id_from_jwt)],
    api_key_data: Annotated[APIKey | None, Depends(get_current_api_key_data)]
) -> str:
    """
    Primary authentication dependency.
    Prioritizes JWT, falls back to API key.
    Raises 401 if neither is valid.
    """
    # If JWT is present and valid, use it (user access)
    if jwt_user_id:
        return jwt_user_id
        
    # If API key is present and valid, use its associated user_id (service access)
    if api_key_data:
        return api_key_data.user_id
        
    # If neither is valid, raise unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide a valid JWT token or x-api-key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_user_id_with_permission(
    permission: APIKeyPermissions,
    jwt_user_id: Annotated[str | None, Depends(get_current_user_id_from_jwt)],
    api_key_data: Annotated[APIKey | None, Depends(get_current_api_key_data)]
) -> str:
    """
    Authentication dependency that also checks for required API key permission.
    JWT users are always granted access.
    """
    # 1. Check JWT first (JWT users have all permissions)
    if jwt_user_id:
        return jwt_user_id
        
    # 2. Check API Key
    if api_key_data:
        if permission in api_key_data.permissions:
            return api_key_data.user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API Key does not have the required '{permission}' permission.",
            )
            
    # 3. If neither, raise unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide a valid JWT token or x-api-key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Specific permission dependencies
async def get_user_id_for_deposit(
    jwt_user_id: Annotated[str | None, Depends(get_current_user_id_from_jwt)],
    api_key_data: Annotated[APIKey | None, Depends(get_current_api_key_data)]
) -> str:
    return await get_user_id_with_permission(APIKeyPermissions.DEPOSIT, jwt_user_id, api_key_data)

async def get_user_id_for_transfer(
    jwt_user_id: Annotated[str | None, Depends(get_current_user_id_from_jwt)],
    api_key_data: Annotated[APIKey | None, Depends(get_current_api_key_data)]
) -> str:
    return await get_user_id_with_permission(APIKeyPermissions.TRANSFER, jwt_user_id, api_key_data)

async def get_user_id_for_read(
    jwt_user_id: Annotated[str | None, Depends(get_current_user_id_from_jwt)],
    api_key_data: Annotated[APIKey | None, Depends(get_current_api_key_data)]
) -> str:
    return await get_user_id_with_permission(APIKeyPermissions.READ, jwt_user_id, api_key_data)


