import hashlib
from datetime import datetime, timedelta, timezone

from core.config import settings
from schemas.auth import TokenData

try:
    import jwt as pyjwt

    _USE_PYJWT = True
except ImportError:
    from jose import jwt as jose_jwt

    _USE_PYJWT = False


def verify_api_key_hash(key: str, key_hash: str) -> bool:
    """Verify a raw API key against its SHA-256 hash."""
    return hash_api_key(key) == key_hash


def hash_api_key(key: str) -> str:
    """Hash long API keys using SHA-256 instead of bcrypt."""
    return hashlib.sha256(key.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "sub": "access"})
    if _USE_PYJWT:
        return pyjwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
    return jose_jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenData | None:
    try:
        if _USE_PYJWT:
            payload = pyjwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        else:
            payload = jose_jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        if user_id is None or email is None:
            return None
        return TokenData(user_id=user_id, email=email)
    except Exception:
        return None
