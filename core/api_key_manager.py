import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models import APIKey
from core.security import hash_api_key, verify_api_key_hash   # <-- USE SHA-256 HASHING HERE
from schemas.keys import APIKeyPermissions


# ---------------- EXPIRY PARSER ---------------- #

def parse_expiry(expiry_str: str) -> timedelta:
    """Converts expiry string (e.g., '1H', '1D') to a timedelta object."""
    unit = expiry_str[-1].upper()
    value = int(expiry_str[:-1])
    
    match unit:
        case 'H':
            return timedelta(hours=value)
        case 'D':
            return timedelta(days=value)
        case 'M':
            return timedelta(days=value * 30)
        case 'Y':
            return timedelta(days=value * 365)
        case _:
            raise ValueError("Invalid expiry format. Use 1H, 1D, 1M, or 1Y.")


# ---------------- CREATE API KEY ---------------- #

async def generate_api_key(
    db: AsyncSession,
    user_id: str,
    name: str,
    permissions: List[str],
    expiry_str: str
) -> Dict[str, Any]:

    # 1. Limit check
    stmt = select(APIKey).where(
        APIKey.user_id == user_id,
        APIKey.is_active == True,
        APIKey.expires_at > datetime.utcnow()
    )
    active_keys = (await db.execute(stmt)).scalars().all()

    if len(active_keys) >= 5:
        raise ValueError("Maximum of 5 active API keys allowed per user.")

    # 2. Validate permissions
    for perm in permissions:
        if perm not in APIKeyPermissions.ALL:
            raise ValueError(f"Invalid permission: {perm}")

    # 3. Expiry
    expires_at = datetime.utcnow() + parse_expiry(expiry_str)

    # 4. Generate raw key
    raw_key = f"sk_live_{uuid.uuid4().hex}"

    # 5. Hash using SHA-256 (NOT bcrypt)
    key_hash = hash_api_key(raw_key)

    # 6. Save
    new_key = APIKey(
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        permissions=permissions,
        expires_at=expires_at,
        is_active=True
    )

    db.add(new_key)
    await db.flush()

    return {
        "api_key": raw_key,      # Only returned ONE time
        "expires_at": expires_at
    }


# ---------------- LOOKUP API KEY ---------------- #

async def get_api_key_data(db: AsyncSession, raw_key: str) -> APIKey | None:
    """Retrieve and validate API key."""
    
    hashed = hash_api_key(raw_key)

    # Much more efficient: lookup by hash directly
    stmt = select(APIKey).where(APIKey.is_active == True)
    result = await db.execute(stmt)
    active_keys = result.scalar_one_or_none()

    for key_data in active_keys:
        if verify_api_key_hash(raw_key, key_data.key_hash):
            
            # Check if expired
            if key_data.expires_at < datetime.utcnow():
                # Optionally, deactivate the key here
                return None # Key expired
            
            return key_data

    return None


# ---------------- ROLLOVER API KEY ---------------- #

async def rollover_api_key(db: AsyncSession, expired_key_id: str, expiry_str: str) -> Dict[str, Any]:

    stmt = select(APIKey).where(APIKey.id == expired_key_id)
    old_key = (await db.execute(stmt)).scalar_one_or_none()

    if not old_key:
        raise ValueError("Expired key ID not found.")

    if old_key.expires_at > datetime.utcnow():
        raise ValueError("Key is not yet expired and cannot be rolled over.")

    # Deactivate old key
    old_key.is_active = False

    # Create new key with original permissions
    return await generate_api_key(
        db=db,
        user_id=old_key.user_id,
        name=f"Rollover of {old_key.name}",
        permissions=old_key.permissions,
        expiry_str=expiry_str
    )