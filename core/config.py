import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import make_url

load_dotenv()

SQLITE_TMP_PATH = "sqlite+aiosqlite:////tmp/fast_wallet.db"


def normalize_database_url(raw_url: str | None) -> str:
    """
    Ensure DATABASE_URL is valid for SQLAlchemy async.

    - Accepts common Postgres prefixes and upgrades to asyncpg.
    - Falls back to /tmp SQLite if missing or invalid to avoid
      read-only FS issues on Vercel.
    """
    if not raw_url or not raw_url.strip():
        return SQLITE_TMP_PATH

    url = raw_url.strip()

    # Normalize heroku-style prefix
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    # Ensure async driver for Postgres
    if url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        url = "postgresql+asyncpg://" + url.split("://", 1)[1]

    # Validate URL; on failure, fall back to /tmp SQLite
    try:
        make_url(url)
        return url
    except Exception:
        # Log to stdout; Vercel surfaces this in logs
        print("Invalid DATABASE_URL provided; falling back to /tmp SQLite.")
        return SQLITE_TMP_PATH

class Settings(BaseSettings):
    # General
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Paystack
    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_mock")
    PAYSTACK_PUBLIC_KEY: str = os.getenv("PAYSTACK_PUBLIC_KEY", "pk_test_mock")
    PAYSTACK_WEBHOOK_SECRET: str = os.getenv("PAYSTACK_WEBHOOK_SECRET", "webhook-secret-mock")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    ## Use an env-provided database first. Default to /tmp so Vercel's
# read-only filesystem doesn't break SQLite at startup.
    DATABASE_URL: str = normalize_database_url(os.getenv("DATABASE_URL"))

    # Google OAuth (Mocked)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "mock-client-id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "mock-client-secret")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

settings = Settings()

