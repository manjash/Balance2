from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


# Shared properties
class TransactionEventBase(BaseModel):
    transaction_id: UUID = None
    type: str = None
    amount: float = None
    currency: str = None
    category: str = None
    user_id: UUID = None
    gateway_id: str = None


# Properties to receive via API on creation
class TransactionEventCreate(TransactionEventBase):
    transaction_id: UUID
    type: str
    amount: float
    currency: str
    category: str
    user_id: UUID
    gateway_id: str


# Properties to receive via API on update
class TransactionEventUpdate(TransactionEventBase):
    original: None
    transaction_id: UUID = None
    type: str = None
    amount: float = None
    currency: str = None
    category: str = None
    user_id: UUID = None
    gateway_id: str = None


class TransactionEventInDBBase(TransactionEventBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class TransactionEvent(TransactionEventInDBBase):
    transaction_id: UUID = Field(default=False)
    type: str = Field(default=False)
    amount: float = Field(default=False)
    currency: str = Field(default=False)
    category: str = Field(default=False)
    user_id: UUID = Field(default=False)
    gateway_id: str = Field(default=False)

    class Config:
        allow_population_by_field_name = True
