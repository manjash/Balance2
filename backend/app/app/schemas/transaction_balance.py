from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


# Shared properties
class TransactionBalanceBase(BaseModel):
    transaction_id: UUID = None
    balance_id: UUID = None


# Properties to receive via API on creation
class TransactionBalanceCreate(TransactionBalanceBase):
    transaction_id: UUID
    balance_id: UUID


# Properties to receive via API on update
class TransactionBalanceUpdate(TransactionBalanceBase):
    original: None
    transaction_id: UUID = None
    balance_id: UUID = None


class TransactionBalanceInDBBase(TransactionBalanceBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class TransactionBalance(TransactionBalanceInDBBase):
    transaction_id: UUID = Field(default=False)
    balance_id: UUID = Field(default=False)

    class Config:
        allow_population_by_field_name = True
