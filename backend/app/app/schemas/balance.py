from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


# Shared properties
class BalanceBase(BaseModel):
    user_id: UUID = None
    amount: float = None
    amount_reserved: Optional[float] = None


# Properties to receive via API on creation
class BalanceCreate(BalanceBase):
    user_id: UUID
    amount: float
    amount_reserved: Optional[float]


# Properties to receive via API on update
class BalanceUpdate(BalanceBase):
    user_id: UUID = None
    amount: float = None
    amount_reserved: Optional[float] = None


class BalanceInDBBase(BalanceBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Balance(BalanceInDBBase):
    user_id: UUID = Field(default=False)
    amount: float = Field(default=False)
    amount_reserved: float = Field(default=False)

    class Config:
        allow_population_by_field_name = True
