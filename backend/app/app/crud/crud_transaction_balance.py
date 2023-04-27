from __future__ import annotations
from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any

from app.crud.base import CRUDBase
from app.models.transaction_balance import TransactionBalance
from app.schemas.transaction_balance import TransactionBalanceCreate, TransactionBalanceUpdate
from uuid import UUID as uuid_UUID


class CRUDTransactionEvent(CRUDBase[TransactionBalance, TransactionBalanceCreate, TransactionBalanceUpdate]):
    # Everything is user-dependent
    def get_by_id(self, db: Session, *, id: uuid_UUID) -> Optional[TransactionBalance]:
        return db.query(TransactionBalance).filter(TransactionBalance.id == id).first()

    def get_by_transaction_id(self, db: Session, *, transaction_id: uuid_UUID) -> Optional[TransactionBalance]:
        return db.query(TransactionBalance).filter(TransactionBalance.transaction_id == transaction_id).first()

    def create(self, db: Session, *,
               obj_in: TransactionBalanceCreate,
               ) -> TransactionBalance:
        db_obj = TransactionBalance(
            transaction_id=obj_in.transaction_id,
            balance_id=obj_in.balance_id,
        )
        return super().create(db, obj_in=db_obj)

    def update(self, db: Session, *, db_obj: TransactionBalance, obj_in: Union[TransactionBalanceUpdate, Dict[str, Any]]
               ) -> TransactionBalance:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)


transaction_balance = CRUDTransactionEvent(TransactionBalance)
