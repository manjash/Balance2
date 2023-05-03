from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Order  # noqa: F401
    from . import ServiceProduct


class OrderServiceProducts(Base):
    __tablename__ = "order_service_products"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("order.id"))
    service_product_id = Column(UUID(as_uuid=True), ForeignKey("service_product.id"))
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # authorised, captured, refunded, cancelled (??)
    order: Mapped["Order"] = relationship(back_populates="order_service_product")
    service_product: Mapped[list["ServiceProduct"]] = relationship(back_populates="order_service_product")
