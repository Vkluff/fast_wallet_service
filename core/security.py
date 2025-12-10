import hashlib
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from core.config import settings
from schemas.auth import TokenData


def verify_api_key_hash(key: str, key_hash: str) -> bool:
    """Verify a raw API key against its SHA-256 hash."""
    return hash_api_key(key) == key_hash


def hash_api_key(key: str) -> str:
    """Hash long API keys using SHA-256 instead of bcrypt."""
    return hashlib.sha256(key.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        if user_id is None or email is None:
            return None
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        return None
