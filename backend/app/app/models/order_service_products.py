from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4


from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Order, ServiceProduct  # noqa: F401


class OrderServiceProduct(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    order_id = Column(String, ForeignKey("order.id"))
    service_product_id = Column(String, ForeignKey("service_product.id"))
    order: Mapped["Order"] = relationship(back_populates="order_service_product")
    service_product: Mapped[list["ServiceProduct"]] = relationship(back_populates="order_service_product")

