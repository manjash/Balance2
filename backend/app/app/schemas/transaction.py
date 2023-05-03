from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Shared properties
class TransactionBase(BaseModel):
    gateway: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    data: Optional[str] = None


# Properties to receive via API on creation
class TransactionCreate(TransactionBase):
    # transaction part
    gateway: str
    method: str
    description: str
    data: dict
    # transaction_event part


# Properties to receive via API on update
class TransactionUpdate(TransactionBase):
    original: None
    gateway: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None


class TransactionInDBBase(TransactionBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Transaction(TransactionInDBBase):
    gateway: str = Field(default=False)
    method: str = Field(default=False)
    description: str = Field(default=False)
    data: dict = Field(default=False)

    class Config:
        allow_population_by_field_name = True
