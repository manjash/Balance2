from typing import Any, List, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas

from app.api import deps
from uuid import UUID
from . import users
from app.core.config import settings
from app.core import security
from app.utilities import (
    send_new_account_email,
)

router = APIRouter()


@router.post("/", response_model=schemas.Balance)
def create_balance_by_user_id(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_id: str = Body(...),
) -> Any:
    """
    Create new account an existing user.
    """
    if current_user and current_user.is_superuser:
        balance_in = schemas.BalanceCreate(user_id=UUID(user_id), amount=0)
        balance = crud.balance.create(db, obj_in=balance_in)
        return balance
    else:
        raise HTTPException(
            status_code=400,
            detail="Operation is unavailable.",
        )


@router.post("/getBalance", response_model=schemas.Balance)
def get_balance_by_user_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
) -> Any:
    """
    Return balance of an existing user.
    """

    if users.user_in_DB(db=db, user_id=user_id):
        return crud.balance.get_by_user_id(db, user_id=user_id)


@router.post("/internalTransfer", response_model=Tuple[schemas.Balance, schemas.Balance])
def balance_to_balance_transaction(
    *,
    db: Session = Depends(deps.get_db),
    from_user_id: str = Body(...),
    to_user_id: str = Body(...),
    amount: int = Body(...),
) -> Any:
    """
    Make a transfer from the one user balance to a another user balance.
    """
    from_balance_id = crud.balance.get_by_user_id(db, user_id=UUID(from_user_id)).id
    to_balance_id = crud.balance.get_by_user_id(db, user_id=UUID(to_user_id)).id

    if not from_balance_id or not to_balance_id:
        raise HTTPException(
            status_code=400,
            detail="Account for balance_id=%s or balance_id=%s is not registered." % (from_balance_id, to_balance_id),
        )
    return crud.balance.balance_to_balance_transfer(db,
                                                    from_balance_id,
                                                    to_balance_id,
                                                    amount
                                                    )


@router.post("/moneyIn", response_model=schemas.Balance)
def add_to_balance(
        *,
        db: Session = Depends(deps.get_db),
        user_id: str = Body(...),
        amount: int = Body(...),
) -> Any:
    balance = crud.balance.get_by_user_id(db, user_id=UUID(user_id))
    if not balance:
        raise HTTPException(
            status_code=400,
            detail="Account for user_id=%s is not registered." % user_id,
        )
    return crud.balance.balance_money_update(db, balance_id=balance.id, amount=amount)


@router.post("/moneyOut", response_model=schemas.Balance)
def withdraw_from_balance(
        *,
        db: Session = Depends(deps.get_db),
        user_id: str = Body(...),
        amount: int = Body(...),
) -> Any:
    return add_to_balance(db=db, user_id=user_id, amount=-amount)


@router.post("/reserve", response_model=schemas.Balance)
def reserve(*,
            db: Session = Depends(deps.get_db),
            user_id: str = Body(...),
            service_product_id: str = Body(...),
            order_id: str = Body(...),
            amount: int = Body(...),
            ) -> Any:
    balance = crud.balance.get_by_user_id(db, user_id=UUID(user_id))
    if not balance:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't exist or doesn't have enough funds",
        )
    balance = crud.balance.balance_reserve(db,
                                           balance_id=balance.id,
                                           amount_reserved=amount
                                           )
    transaction = crud.transaction.create(db,
                                          obj_in=schemas.TransactionCreate(
                                              gateway='internal',
                                              method='internal',
                                              description='Service sale from user balance',
                                              data=''
                                          ))
    transaction_event = crud.transaction_event.create(db,
                                                      obj_in=schemas.TransactionEventCreate(
                                                          transaction_id=transaction.id,
                                                          type='authorization',
                                                          amount=amount,
                                                          category='internal_out',
                                                          user_id=user_id,
                                                          gateway_id='internal'
                                                      ))
    transaction_balance_link = crud.transaction_event.\
        link_transaction_balance(db,
                                 transaction_id=transaction.id,
                                 balance_id=balance.id)



@router.post("/reserve/capture", response_model=schemas.Balance)
def reserve_capture(*,
            db: Session = Depends(deps.get_db),
            user_id: str = Body(...),
            amount: int = Body(...),
            ) -> Any:
    balance = crud.balance.get_by_user_id(db, user_id=UUID(user_id))
    if not balance:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't exist or doesn't have enough funds",
        )
    return crud.balance.balance_reserve_captured(db,
                                                 balance_id=balance.id,
                                                 amount=amount
                                                 )


@router.post("/reserve/refund", response_model=schemas.Balance)
def reserve_refund(*,
            db: Session = Depends(deps.get_db),
            user_id: str = Body(...),
            amount: int = Body(...),
            ) -> Any:
    balance = crud.balance.get_by_user_id(db, user_id=UUID(user_id))
    if not balance:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't exist or doesn't have enough funds",
        )
    return crud.balance.balance_reserve_refund(db,
                                               balance_id=balance.id,
                                               amount=amount
                                               )
