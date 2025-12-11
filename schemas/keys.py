from pydantic import BaseModel, Field
from schemas.common import ORMBase
from typing import List
from datetime import datetime

class APIKeyPermissions:
    """Defines the allowed permissions for API keys."""
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    READ = "read"
    ALL = [DEPOSIT, TRANSFER, READ]

class APIKeyCreate(BaseModel):
    name: str = Field(..., description="A human-readable name for the API key.")
    permissions: List[str] = Field(..., description="List of permissions (e.g., ['deposit', 'transfer', 'read']).")
    expiry: str = Field(..., description="Expiry duration (e.g., '1H', '1D', '1M', '1Y').")

class APIKeyResponse(ORMBase):
    api_key: str = Field(..., description="The newly generated API key.")
    expires_at: datetime = Field(..., description="The expiration date and time.")

class APIKeyDetail(ORMBase):
    """Schema for listing API key metadata (excluding the raw key)."""
    id: str
    name: str
    permissions: List[str]
    expires_at: datetime
    is_active: bool

class APIKeyListResponse(BaseModel):
    """Response model for the /keys/list endpoint."""
    keys: List[APIKeyDetail]

class APIKeyRollover(BaseModel):
    expired_key_id: str = Field(..., description="The ID of the expired key to rollover.")
    expiry: str = Field(..., description="New expiry duration (e.g., '1H', '1D', '1M', '1Y').")



