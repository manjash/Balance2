from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, DateTime, Float, String
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4


from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Transaction  # noqa: F401
    from . import User  # noqa: F401


class TransactionEvent(Base):
    __tablename__ = "transaction_event"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transaction.id"), nullable=False)
    type = Column(String, nullable=False)  # authorization, capture, refund
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default='GBP')
    # Categories: payin, payout, internal_in (receive to balance), internal_out (withdraw from balance)
    category = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    gateway_id = Column(String)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    transaction = relationship("Transaction", back_populates='transaction_event')
    user: Mapped["User"] = relationship(back_populates='transaction_event')
