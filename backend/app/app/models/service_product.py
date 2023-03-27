from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4


from app.db.base_class import Base

if TYPE_CHECKING:
    from . import OrderServiceProduct  # noqa: F401


class ServiceProduct(Base):
    __tablename__ = "service_product"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)  # liter, item, kg etc
    order_service_product: Mapped["OrderServiceProduct"] = relationship(back_populates="service_product")

