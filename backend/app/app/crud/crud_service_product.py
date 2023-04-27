from __future__ import annotations
from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any

from app.crud.base import CRUDBase
from app.models.service_product import ServiceProduct
from app.schemas.service_product import ServiceProductCreate, ServiceProductUpdate
from uuid import UUID as uuid_UUID


class CRUDServiceProduct(CRUDBase[ServiceProduct, ServiceProductCreate, ServiceProductUpdate]):
    # Everything is user-dependent
    def get_by_id(self, db: Session, *, service_product_id: uuid_UUID) -> Optional[ServiceProduct]:
        return db.query(ServiceProduct).filter(ServiceProduct.id == service_product_id).first()

    def create(self, db: Session, *,
               obj_in: ServiceProductCreate,
               ) -> ServiceProduct:
        db_obj = ServiceProduct(
            title=obj_in.title,
            description=obj_in.description,
            price=obj_in.price,
            unit=obj_in.unit,
        )
        return super().create(db, obj_in=db_obj)

    def update(self, db: Session, *, db_obj: ServiceProduct, obj_in: Union[ServiceProductUpdate, Dict[str, Any]]
               ) -> ServiceProduct:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)


service_product = CRUDServiceProduct(ServiceProduct)
