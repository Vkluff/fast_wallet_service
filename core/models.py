from typing import List
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # Relationships
    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)
    api_keys: Mapped[List["APIKey"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"
    
class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    wallet_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="wallet")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="wallet")

    def __repr__(self) -> str:
        return f"Wallet(id={self.id!r}, user_id={self.user_id!r}, balance={self.balance!r})"

class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    key_hash: Mapped[str] = mapped_column(String)
    permissions: Mapped[List[str]] = mapped_column(JSON) # Stored as JSON array
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")

    def __repr__(self) -> str:
        return f"APIKey(id={self.id!r}, name={self.name!r}, user_id={self.user_id!r})"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"))
    reference: Mapped[str] = mapped_column(String, unique=True, index=True)
    type: Mapped[str] = mapped_column(String) # 'deposit', 'transfer_out', 'transfer_in'
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String) # 'pending', 'success', 'failed'
    meta: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"Transaction(id={self.id!r}, reference={self.reference!r}, status={self.status!r})"


   