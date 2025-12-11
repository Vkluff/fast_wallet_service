from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.models import Base

# Create the asynchronous engine
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"ssl": True} if settings.DATABASE_URL.startswith("postgresql+asyncpg") else {}
)
# Create the asynchronous session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
async def init_db():
    """This function creates all your tables (User, Wallet, etc.) when the app starts"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
