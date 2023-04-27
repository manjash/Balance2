from __future__ import annotations
from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any
from sqlalchemy import func
from sqlalchemy.sql import extract

from app.crud.base import CRUDBase
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from uuid import UUID as uuid_UUID


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    # Everything is user-dependent
    def get_by_id(self, db: Session, *, order_id: uuid_UUID) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    def create(self, db: Session, *,
               obj_in: OrderCreate,
               ) -> Order:
        db_obj = Order(
            transaction_id=obj_in.transaction_id,
            status=obj_in.status,
            amount=obj_in.amount,
        )
        return super().create(db, obj_in=db_obj)

    def update(self, db: Session, *, db_obj: Order, obj_in: Union[OrderUpdate, Dict[str, Any]]) -> Order:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def filter_by_date(self, db: Session, *, yyyymm: str):
        if len(yyyymm) != 6 or not int(yyyymm):
            raise ValueError("Please provide date in format yyyymm")
        ids = db.query(Order.id).filter(extract('year', func.date(Order.created)) == yyyymm[:4],
                                        extract('month', func.date(Order.created)) == yyyymm[4:6]
                                        ).all()
        return [elem[0] for elem in ids]

    def close_session(self, db: Session):
        db.close()


order = CRUDOrder(Order)
