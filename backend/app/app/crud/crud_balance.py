from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union
from uuid import UUID as uuid_UUID

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.balance import Balance
from app.schemas.balance import BalanceCreate, BalanceUpdate


class CRUDBalance(CRUDBase[Balance, BalanceCreate, BalanceUpdate]):
    # Everything is user-dependent
    def get_by_user_id(self, db: Session, *, user_id: uuid_UUID, with_lock=False) -> Optional[Balance]:
        if not with_lock:
            db_obj = db.query(Balance).filter(Balance.user_id == user_id).first()
        else:
            db_obj = db.query(Balance).with_for_update().filter(Balance.user_id == user_id).first()
        if not db_obj:
            raise HTTPException(status_code=400, detail="The user doesn't have a balance account")
        return db_obj

    def get_by_balance_id(self, db: Session, *, balance_id: uuid_UUID, with_lock=False) -> Optional[Balance]:
        if not with_lock:
            db_obj = db.query(Balance).filter(Balance.id == balance_id).first()
        else:
            db_obj = db.query(Balance).with_for_update().filter_by(id=balance_id).first()
        if not db_obj:
            raise HTTPException(status_code=400, detail="The user doesn't have a balance account")
        return db_obj

    def create(self, db: Session, *, obj_in: BalanceCreate) -> Balance:
        db_obj = db.query(self.model).filter(self.model.user_id == obj_in.user_id).first()
        if db_obj:
            raise HTTPException(status_code=400, detail="Balance account already registered for the user.")
        db_obj = Balance(
            user_id=obj_in.user_id,
            amount=obj_in.amount,
        )
        return super().create(db, obj_in=db_obj)

    def update(self, db: Session, *, db_obj: Balance, obj_in: Union[BalanceUpdate, Dict[str, Any]]) -> Balance:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "amount" in update_data.keys() and update_data["amount"] < 0:
            raise HTTPException(status_code=400, detail="Balance can't be updated to negative")
        if "amount_reserved" in update_data.keys() and update_data["amount_reserved"] < 0:
            raise HTTPException(status_code=400, detail="Reserved balance can't be updated to negative")
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def balance_to_balance_transfer(
        self,
        db: Session,
        from_user_id: UUID,
        to_user_id: UUID,
        amount: float,
    ) -> Tuple[Balance, Balance]:

        balance_from = self.get_by_user_id(db, user_id=from_user_id, with_lock=True)
        if balance_from.amount < amount:
            raise HTTPException(status_code=400, detail="Not enough funds to make a transfer")
        balance_from.amount -= amount
        balance_to = self.get_by_user_id(db, user_id=to_user_id, with_lock=True)
        balance_to.amount += amount
        db.add(balance_from)
        db.add(balance_to)
        db.commit()
        db.refresh(balance_from)
        db.refresh(balance_to)
        return balance_from, balance_to

    def close_session(self, db: Session):
        db.close()


balance = CRUDBalance(Balance)
