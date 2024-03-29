from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Balance  # noqa: F401


class TransactionBalance(Base):
    __tablename__ = "transaction_balance"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    balance_id = Column(UUID(as_uuid=True), ForeignKey("balance.id"))
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transaction.id"))
    last_update = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=True)
    transaction = relationship("Transaction", back_populates="transaction_balance")
    balance = relationship("Balance", back_populates="transaction_balance")
