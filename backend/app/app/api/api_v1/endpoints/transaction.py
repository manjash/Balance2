from typing import Any, Tuple
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

from .balance import add_to_balance

router = APIRouter()


@router.post("/", response_model=Tuple[schemas.Transaction, schemas.TransactionEvent])
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    gateway: str = Body(...),
    method: str = Body(...),
    description: str = Body(...),
    data: dict = Body(...),
    type: str = Body(...),
    amount: float = Body(...),
    currency: str = Body(...),
    category: str = Body(...),
    user_id: str = Body(...),
    gateway_id: str = Body(...),
) -> Any:
    """
    Create a new transaction.
    """
    transaction_in = schemas.TransactionCreate(
        gateway=gateway,
        method=method,
        description=description,
        data=data,
    )
    transaction = crud.transaction.create(db, obj_in=transaction_in)
    transaction_event_in = schemas.TransactionEventCreate(
        transaction_id=transaction.id,
        type=type,
        amount=amount,
        currency=currency,
        category=category,
        user_id=UUID(user_id),
        gateway_id=gateway_id,
    )
    transaction_event = crud.transaction_event.create(db, obj_in=transaction_event_in)
    return transaction, transaction_event


"""
We already have a transaction in a type=captured state, the money is on the
company's account. Now money has to be added to the user's account -->
We'll send user_id, amount. And want to see balance before and after

"""


@router.post("/captured_to_balance", response_model=Tuple[schemas.Balance, schemas.TransactionEvent])
def captured_money_to_balance(
    *,
    db: Session = Depends(deps.get_db),
    transaction_id: str = Body(...),
) -> Any:
    """
    Add money to balance and link a transaction to balance that receives the money.
    status of the transaction (captured or not) checked by some other service
    """

    transaction_in = crud.transaction_event.get_by_transaction_id(db, transaction_id=transaction_id)
    balance_in = add_to_balance(db=db, user_id=str(transaction_in.user_id), amount=transaction_in.amount)[1]
    crud.transaction_balance.create(
        db,
        obj_in=schemas.TransactionBalance(
            transaction_id=transaction_id,
            balance_id=balance_in.id,
        ),
    )
    return balance_in, transaction_in
