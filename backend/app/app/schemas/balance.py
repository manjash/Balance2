from typing import Optional
from pydantic import BaseModel, Field, constr, validator
from uuid import UUID


# class UserLogin(BaseModel):
#     username: str
#     password: str


# Shared properties
class BalanceBase(BaseModel):
    user_id: UUID = None
    amount: int = None
    amount_reserved: Optional[int] = None


# Properties to receive via API on creation
class BalanceCreate(BalanceBase):
    user_id: UUID
    amount: int
    amount_reserved: Optional[int]


# Properties to receive via API on update
class BalanceUpdate(BalanceBase):
    original: None
    user_id: None
    amount: None
    amount_reserved: Optional[int] = None


class BalanceInDBBase(BalanceBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Balance(BalanceInDBBase):
    user_id: UUID = Field(default=False)
    amount: int = Field(default=False)
    amount_reserved: int = Field(default=False)

    class Config:
        allow_population_by_field_name = True

#
# # Additional properties stored in DB
# class BalanceInDB(BalanceInDBBase):
#     user_id: UUID = None
