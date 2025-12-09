import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

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

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

    # Google OAuth (Mocked)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "mock-client-id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "mock-client-secret")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

settings = Settings()

