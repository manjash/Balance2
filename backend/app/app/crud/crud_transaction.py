from __future__ import annotations
from sqlalchemy.orm import Session
# from typing import List
from typing import Optional, Union, Dict, Any, Tuple
# from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import UUID

from app.crud.base import CRUDBase
from app.models.transaction import Transaction
from app.models.transaction_event import TransactionEvent
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.schemas.transaction_event import TransactionEventCreate
from uuid import UUID as uuid_UUID
import json


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    # Everything is user-dependent
    def get_by_id(self, db: Session, *, transaction_id: uuid_UUID) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def create(self, db: Session, *,
               obj_in: TransactionCreate,
               ) -> Transaction:
        db_obj = Transaction(
            gateway=obj_in.gateway,
            method=obj_in.method,
            description=obj_in.description,
            data=obj_in.data,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update(self, db: Session, *, db_obj: Transaction, obj_in: Union[TransactionUpdate, Dict[str, Any]]) -> Transaction:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)



transaction = CRUDTransaction(Transaction)
