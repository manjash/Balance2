from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4


from app.db.base_class import Base

if TYPE_CHECKING:
    from . import User, TransactionBalance  # noqa: F401


class Balance(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    amount = Column(Float, nullable=True)
    amount_reserved = Column(Float, nullable=True, default=0)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=True)
    user = relationship("User", back_populates="balance")
    transaction_balance = relationship("TransactionBalance", back_populates='balance')
