from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps


router = APIRouter()


@router.post("/", response_model=schemas.ServiceProduct)
def create_service_product(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Body(...),
    description: str = Body(...),
    price: float = Body(...),
    unit: str = Body(...),

) -> Any:
    """
    Create a new transaction.
    """
    service_product_in = schemas.ServiceProductCreate(title=title,
                                                      description=description,
                                                      price=price,
                                                      unit=unit,
                                                      )
    return crud.service_product.create(db, obj_in=service_product_in)
