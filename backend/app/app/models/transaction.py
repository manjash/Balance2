from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4


from app.db.base_class import Base

if TYPE_CHECKING:
    from . import TransactionEvent, TransactionBalance, Order  # noqa: F401


class Transaction(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    gateway = Column(String, nullable=False)    # stripe, paypal, adyen, internal
    method = Column(String, nullable=False)     # card, ideal, paypal, internal
    description = Column(String, nullable=False)
    data = Column(JSON, nullable=True)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    transaction_event = relationship("TransactionEvent", back_populates='transaction')
    transaction_balance = relationship("TransactionBalance", back_populates='transaction')
    order = relationship("Order", back_populates='transaction')
