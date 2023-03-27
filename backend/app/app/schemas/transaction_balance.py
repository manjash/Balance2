from typing import Optional
from pydantic import BaseModel, Field, constr, validator
from uuid import UUID


# class UserLogin(BaseModel):
#     username: str
#     password: str


# Shared properties
class TransactionBalanceBase(BaseModel):
    transaction_id: UUID = None
    balance_id: UUID = None


# Properties to receive via API on creation
class TransactionBalanceCreate(TransactionBalanceBase):
    transaction_id: UUID
    balance_id: int


# Properties to receive via API on update
class TransactionBalanceUpdate(TransactionBalanceBase):
    original: None
    transaction_id: None
    balance_id: None


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

#
# # Additional properties stored in DB
# class BalanceInDB(BalanceInDBBase):
#     user_id: UUID = None
