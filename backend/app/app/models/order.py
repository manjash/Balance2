from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import OrderServiceProducts  # noqa: F401


class Order(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transaction.id"))
    status = Column(String, nullable=False)  # pending, confirmed, shipped, delivered, returned
    amount = Column(Float, nullable=False)  # total price of the order, all items included
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    transaction = relationship("Transaction", back_populates="order")
    order_service_product: Mapped[list["OrderServiceProducts"]] = relationship(back_populates="order")
