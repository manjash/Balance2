from __future__ import annotations

from typing import Any, Dict, Optional, Union
from uuid import UUID as uuid_UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.transaction_event import TransactionEvent
from app.schemas.transaction_event import TransactionEventCreate, TransactionEventUpdate


class CRUDTransactionEvent(CRUDBase[TransactionEvent, TransactionEventCreate, TransactionEventUpdate]):
    # Everything is user-dependent
    def get_by_id(self, db: Session, *, transaction_event_id: uuid_UUID) -> Optional[TransactionEvent]:
        return db.query(TransactionEvent).filter(TransactionEvent.id == transaction_event_id).first()

    def get_by_transaction_id(self, db: Session, *, transaction_id: uuid_UUID) -> Optional[TransactionEvent]:
        return db.query(TransactionEvent).filter(TransactionEvent.transaction_id == transaction_id).first()

    def create(
        self,
        db: Session,
        *,
        obj_in: TransactionEventCreate,
    ) -> TransactionEvent:
        db_obj = TransactionEvent(
            transaction_id=obj_in.transaction_id,
            type=obj_in.type,
            amount=obj_in.amount,
            currency=obj_in.currency,
            category=obj_in.category,
            user_id=obj_in.user_id,
            gateway_id=obj_in.gateway_id,
        )
        return super().create(db, obj_in=db_obj)

    def update(
        self, db: Session, *, db_obj: TransactionEvent, obj_in: Union[TransactionEventUpdate, Dict[str, Any]]
    ) -> TransactionEvent:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)


transaction_event = CRUDTransactionEvent(TransactionEvent)
