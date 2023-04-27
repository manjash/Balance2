from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


# Shared properties
class OrderServiceProductsBase(BaseModel):
    order_id: UUID = None
    service_product_id: UUID = None
    price: float = None
    status: str = None


# Properties to receive via API on creation
class OrderServiceProductsCreate(OrderServiceProductsBase):
    order_id: UUID
    service_product_id: UUID
    price: float
    status: str


# Properties to receive via API on update
class OrderServiceProductsUpdate(OrderServiceProductsBase):
    original: None
    order_id: UUID = None
    service_product_id: UUID = None
    price: float = None
    status: str = None


class OrderServiceProductsInDBBase(OrderServiceProductsBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class OrderServiceProducts(OrderServiceProductsInDBBase):
    order_id: UUID = Field(default=False)
    service_product_id: UUID = Field(default=False)
    price: float = Field(default=False)
    status: str = Field(default=False)

    class Config:
        allow_population_by_field_name = True
