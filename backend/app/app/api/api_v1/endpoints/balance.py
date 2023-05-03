import os
from typing import Any, Tuple
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Balance)
def create_balance_by_user_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
    amount: float = Body(default=0),
) -> Any:
    """
    Create new balance account for an existing user.
    """
    balance_in = schemas.BalanceCreate(user_id=UUID(user_id), amount=amount)
    balance = crud.balance.create(db, obj_in=balance_in)
    return balance


@router.get("/getBalance/{user_id}", response_model=schemas.Balance)
def get_balance_by_user_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
) -> Any:
    """
    Return balance of an existing user.
    """
    return crud.balance.get_by_user_id(db, user_id=UUID(user_id))


@router.post("/internalTransfer", response_model=Tuple[schemas.Balance, schemas.Balance])
def balance_to_balance_transaction(
    *,
    db: Session = Depends(deps.get_db),
    from_user_id: str = Body(...),
    to_user_id: str = Body(...),
    amount: float = Body(...),
) -> Any:
    """
    Make a transfer from the one user balance to a another user balance.
    """
    return crud.balance.balance_to_balance_transfer(db, from_user_id, to_user_id, amount)


@router.post("/moneyIn", response_model=schemas.Balance)
def add_to_balance(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
    amount: float = Body(...),
) -> schemas.Balance:
    """
    Increase balance amount.
    """
    balance_locked = crud.balance.get_by_user_id(db, user_id=UUID(user_id), with_lock=True)
    return crud.balance.update(db, db_obj=balance_locked, obj_in={"amount": balance_locked.amount + amount})


@router.post("/moneyOut", response_model=schemas.Balance)
def withdraw_from_balance(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
    amount: float = Body(...),
) -> schemas.Balance:
    """
    Decrease balance amount.
    """
    return add_to_balance(db=db, user_id=user_id, amount=-amount)


@router.post("/reserve", response_model=schemas.Balance)
def reserve(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
    service_product_id: str = Body(...),
    order_id: str = Body(...),
    amount: float = Body(...),
) -> Any:
    """
    Assuming there was an order and transaction registered:
    - reserve some amount off the balance
    - create a link between
        - the transaction and balance operation
        - the order and the service / product the reservation is done for with status = "authorised"
    """
    balance = crud.balance.get_by_user_id(db, user_id=UUID(user_id), with_lock=True)
    obj_in = {"amount": balance.amount - amount, "amount_reserved": balance.amount_reserved + amount}
    balance = crud.balance.update(db, db_obj=balance, obj_in=obj_in)

    transaction_id = crud.order.get_by_id(db, order_id=UUID(order_id)).transaction_id
    crud.transaction_balance.create(
        db,
        obj_in=schemas.TransactionBalanceCreate(
            transaction_id=transaction_id,
            balance_id=balance.id,
        ),
    )
    crud.order_service_products.create(
        db,
        obj_in=schemas.OrderServiceProductsCreate(
            order_id=UUID(order_id),
            service_product_id=UUID(service_product_id),
            price=amount,
            status="authorised",
        ),
    )
    return balance


@router.post("/reserve/capture", response_model=Tuple[schemas.Balance, schemas.OrderServiceProducts])
def reserve_capture(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
    service_product_id: str = Body(...),
    order_id: str = Body(...),
    amount: float = Body(...),
) -> Any:
    """
    - Capture the amount (or part of it) reserved on the balance account
    - For the relevant order product / service link update status = "captured"
    """
    balance_locked = crud.balance.get_by_user_id(db, user_id=UUID(user_id), with_lock=True)
    osp = crud.order_service_products.get_by_order_id_sp_id(
        db,
        order_id=UUID(order_id),
        service_product_id=UUID(service_product_id),
        with_lock=True,
    )
    if osp.price != amount:
        raise HTTPException(
            status_code=400,
            detail="The amount to capture doesn't match the price of the service/product",
        )
    if osp.status != "authorised":
        raise HTTPException(
            status_code=400,
            detail="The amount is not authorised",
        )
    osp.status = "captured"
    balance_locked.amount_reserved -= amount
    db.add(osp)
    db.add(balance_locked)
    db.commit()
    db.refresh(osp)
    db.refresh(balance_locked)
    return balance_locked, osp


@router.post("/reserve/refund", response_model=Tuple[schemas.Balance, schemas.OrderServiceProducts])
def reserve_refund(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str = Body(...),
    service_product_id: str = Body(...),
    order_id: str = Body(...),
    amount: float = Body(...),
) -> Any:

    """
    The method reverts the amount reserved that was authorised but not yet captured
    """
    osp = crud.order_service_products.get_by_order_id_sp_id(
        db,
        order_id=UUID(order_id),
        service_product_id=UUID(service_product_id),
        with_lock=True,
    )
    balance_locked = crud.balance.get_by_user_id(db, user_id=UUID(user_id), with_lock=True)
    osp_status = osp.status
    if osp_status == "authorised":
        balance_locked.amount_reserved -= amount
        balance_locked.amount += amount
    elif osp_status == "captured":
        balance_locked.amount += amount
    else:
        raise HTTPException(
            status_code=400,
            detail="order_service_product.status is incorrect, the balance can't be refunded",
        )
    osp.status = "refunded"
    db.add(balance_locked)
    db.add(osp)
    db.commit()
    db.refresh(balance_locked)
    db.refresh(osp)
    return balance_locked, osp


@router.post("/accountantReport")
def accountant_report(*, db: Session = Depends(deps.get_db), yyyymm: str = Body(...)) -> Any:
    order_ids = crud.order.filter_by_date(db, yyyymm=yyyymm)
    report_data = crud.order_service_products.filter_by_order_ids(db, order_ids=order_ids)
    filename = "accountant_report_%s.csv" % yyyymm
    with open(filename, "w") as f:
        res = "service_title\tamount\n"
        res += "\n".join(["\t".join([title, str(amount)]) for title, amount in report_data])
        f.write(res)
        return os.path.abspath(filename)
