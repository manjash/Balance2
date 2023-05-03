from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import OrderServiceProducts  # noqa: F401


class ServiceProduct(Base):
    __tablename__ = "service_product"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # liter, item, kg etc
    order_service_product: Mapped["OrderServiceProducts"] = relationship(back_populates="service_product")
