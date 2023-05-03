from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Shared properties
class ServiceProductBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None


# Properties to receive via API on creation
class ServiceProductCreate(ServiceProductBase):
    title: str
    description: Optional[str]
    price: float
    unit: str


# Properties to receive via API on update
class ServiceProductUpdate(ServiceProductBase):
    original: None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None


class ServiceProductInDBBase(ServiceProductBase):
    id: Optional[UUID] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class ServiceProduct(ServiceProductInDBBase):
    title: str = Field(default=False)
    description: Optional[str] = Field(default=False)
    price: float = Field(default=False)
    unit: str = Field(default=False)

    class Config:
        allow_population_by_field_name = True
