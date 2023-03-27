from __future__ import annotations
from sqlalchemy.orm import Session
# from typing import List
from typing import Optional, Union, Dict, Any, Tuple
# from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import UUID

from app.crud.base import CRUDBase
from app.models.balance import Balance
from app.schemas.balance import BalanceCreate, BalanceUpdate
from uuid import UUID as uuid_UUID


class CRUDBalance(CRUDBase[Balance, BalanceCreate, BalanceUpdate]):
    # Everything is user-dependent
    def get_by_user_id(self, db: Session, *, user_id: uuid_UUID) -> Optional[Balance]:
        return db.query(Balance).filter(Balance.user_id == user_id).first()

    def get_by_balance_id(self, db: Session, *, balance_id: uuid_UUID) -> Optional[Balance]:
        return db.query(Balance).filter(Balance.id == balance_id).first()

    def get_by_balance_id_with_lock(self, db: Session, *, balance_id: uuid_UUID)-> Optional[Balance]:
        return db.query(Balance).with_for_update().filter_by(id=balance_id).first()

    def create(self, db: Session, *, obj_in: BalanceCreate) -> Balance:
        db_obj = db.query(self.model).filter(self.model.user_id == obj_in.user_id).first()
        if db_obj:
            raise ValueError(f"Balance account already registered for the user.")
        db_obj = Balance(
            user_id=obj_in.user_id,
            amount=obj_in.amount,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Balance, obj_in: Union[BalanceUpdate, Dict[str, Any]]) -> Balance:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def upd_amount_with_lock(self, db, balance_id: UUID, amount_diff: int) -> Balance:
        result = self.get_by_balance_id_with_lock(db, balance_id=balance_id)
        if amount_diff < 0:
            if result.amount < - amount_diff:
                raise ValueError(f"Not enough funds on the balance to lock")
        result.amount += amount_diff
        return result

    def balance_money_update(self, db: Session, balance_id: UUID, amount: int) -> Balance:
        balance_in = self.upd_amount_with_lock(db, balance_id, amount)
        db.add(balance_in)
        db.commit()
        db.refresh(balance_in)
        return balance_in

    def balance_to_balance_transfer(self, db: Session,
                                    balance_from_id: UUID,
                                    balance_to_id: UUID,
                                    amount_diff: int) -> Tuple[Balance, Balance]:
        balance_from = self.upd_amount_with_lock(db, balance_from_id, -amount_diff)
        if balance_from:
            balance_to = self.upd_amount_with_lock(db, balance_to_id, amount_diff)
            db.add(balance_from)
            db.add(balance_to)
            db.commit()
            db.refresh(balance_from)
            db.refresh(balance_to)
            return balance_from, balance_to
        else:
            raise ValueError(f"Not enough funds to withdraw")

    def balance_reserve(self, db: Session,
                        balance_id: UUID,
                        amount_reserved: int
                        ) -> Balance:
        balance_in = self.get_by_balance_id_with_lock(db, balance_id=balance_id)
        if balance_in.amount >= amount_reserved:
            balance_in.amount -= amount_reserved
            balance_in.amount_reserved += amount_reserved
            db.add(balance_in)
            db.commit()
            db.refresh(balance_in)
            return balance_in
        else:
            raise ValueError(f"Not enough funds to withdraw")

    def balance_reserve_captured(self, db: Session,
                              balance_id: UUID,
                              amount: int) -> Balance:
        balance_in = self.get_by_balance_id_with_lock(db, balance_id=balance_id)
        if balance_in.amount_reserved >= amount:
            balance_in.amount_reserved -= amount
            db.add(balance_in)
            db.commit()
            db.refresh(balance_in)
            return balance_in
        else:
            raise ValueError(f"Not enough funds to withdraw in reserve")

    def balance_reserve_refund(self, db: Session,
                                balance_id: UUID,
                                amount: int) -> Balance:
        balance_in = self.get_by_balance_id_with_lock(db, balance_id=balance_id)
        if balance_in.amount_reserved >= amount:
            balance_in.amount += amount
            balance_in.amount_reserved -= amount
            db.add(balance_in)
            db.commit()
            db.refresh(balance_in)
            return balance_in
        else:
            raise ValueError(f"Not enough funds to release")


balance = CRUDBalance(Balance)
