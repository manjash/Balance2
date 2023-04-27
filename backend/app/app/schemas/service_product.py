from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


# Shared properties
class ServiceProductBase(BaseModel):
    title: str = None
    description: Optional[str] = None
    price: float = None
    unit: str = None


# Properties to receive via API on creation
class ServiceProductCreate(ServiceProductBase):
    title: str
    description: Optional[str]
    price: float
    unit: str


# Properties to receive via API on update
class ServiceProductUpdate(ServiceProductBase):
    original: None
    title: str = None
    description: Optional[str] = None
    price: float = None
    unit: str = None


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
