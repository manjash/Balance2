from __future__ import annotations
from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any
from fastapi import HTTPException
from sqlalchemy.sql import functions

from app.crud.base import CRUDBase
from app.models.order_service_products import OrderServiceProducts
from app.models.service_product import ServiceProduct
from app.schemas.order_service_products import OrderServiceProductsCreate, OrderServiceProductsUpdate
from uuid import UUID as uuid_UUID


class CRUDOrderServiceProduct(CRUDBase[OrderServiceProducts, OrderServiceProductsCreate, OrderServiceProductsUpdate]):
    # Everything is user-dependent
    def get_by_id(self, db: Session, *, order_service_product_id: uuid_UUID) -> Optional[OrderServiceProducts]:
        db_obj = db.query(OrderServiceProducts)\
            .filter(OrderServiceProducts.id == order_service_product_id).first()
        if not db_obj:
            raise HTTPException(status_code=400, detail="The order_service_product connection doesn't exist")
        return db_obj

    def get_by_order_id_sp_id(self, db: Session, *, order_id: uuid_UUID, service_product_id: uuid_UUID, with_lock=False
                              ) -> Optional[OrderServiceProducts]:
        if not with_lock:
            db_obj = db.query(OrderServiceProducts)\
                .filter(OrderServiceProducts.order_id == order_id,
                        OrderServiceProducts.service_product_id == service_product_id
                        ).first()
        else:
            db_obj = db.query(OrderServiceProducts).with_for_update() \
                .filter(OrderServiceProducts.order_id == order_id,
                        OrderServiceProducts.service_product_id == service_product_id
                ).first()
        if not db_obj:
            raise HTTPException(status_code=400, detail="The order_service_product connection doesn't exist")
        return db_obj

    def create(self, db: Session, *,
               obj_in: OrderServiceProductsCreate,
               ) -> OrderServiceProducts:
        db_obj = OrderServiceProducts(
            order_id=obj_in.order_id,
            service_product_id=obj_in.service_product_id,
            price=obj_in.price,
            status=obj_in.status,
        )
        return super().create(db, obj_in=db_obj)

    def update(self, db: Session, *, db_obj: OrderServiceProducts,
               obj_in: Union[OrderServiceProductsUpdate, Dict[str, Any]]
               ) -> OrderServiceProducts:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def filter_by_order_ids(self, db: Session, *, order_ids: list):
        return db.query(ServiceProduct.title,
                        functions.sum(OrderServiceProducts.price)
                        )\
            .filter(OrderServiceProducts.service_product_id == ServiceProduct.id,
                    OrderServiceProducts.order_id.in_(order_ids),
                    OrderServiceProducts.status == 'captured'
                    )\
            .group_by(OrderServiceProducts.service_product_id,
                      ServiceProduct.title
                      )\
            .all()


order_service_products = CRUDOrderServiceProduct(OrderServiceProducts)
