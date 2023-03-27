from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4


from app.db.base_class import Base

if TYPE_CHECKING:
    from . import ServiceProduct, Transaction, OrderServiceProduct  # noqa: F401


class Order(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transaction.id"))
    status = Column(String, nullable=False) # pending, confirmed, shipped, delivered, returned
    amount = Column(Integer, nullable=False) # total price of the order, all items included
    transaction = relationship("Transaction", back_populates="order")
    order_service_product: Mapped[list["OrderServiceProduct"]] = relationship(back_populates='order')

