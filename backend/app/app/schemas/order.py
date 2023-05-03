from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Shared properties
class OrderBase(BaseModel):
    transaction_id: Optional[UUID] = None
    amount: Optional[float] = None
    status: Optional[str] = None


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    transaction_id: UUID
    amount: float
    status: str


# Properties to receive via API on update
class OrderUpdate(OrderBase):
    original: None
    transaction_id: Optional[UUID] = None
    amount: Optional[float] = None
    status: Optional[str] = None


class OrderInDBBase(OrderBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Order(OrderInDBBase):
    transaction_id: UUID = Field(default=False)
    amount: float = Field(default=False)
    status: str = Field(default=False)

    class Config:
        allow_population_by_field_name = True
