from typing import Any, List, Tuple

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=Tuple[schemas.Order, List[schemas.OrderServiceProducts]])
def create(
    *,
    db: Session = Depends(deps.get_db),
    transaction_id: str = Body(...),
    amount: float = Body(...),
    service_product_price_ids: dict = Body(...),
) -> Any:
    """
    Create a new order and order_service_product connections.
    """
    order_in = schemas.OrderCreate(transaction_id=transaction_id,
                                   status="pending",
                                   amount=amount,
                                   )
    order = crud.order.create(db, obj_in=order_in)

    osps = []
    for sp_id, sp_price in service_product_price_ids.items():
        obj_in = schemas.OrderServiceProductsCreate(
            order_id=order.id,
            service_product_id=sp_id,
            price=sp_price,
            status="authorised",
        )
        osps.append(crud.order_service_products.create(db, obj_in=obj_in))
    return order, osps


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

    tr_event_in = crud.transaction_event.get_by_transaction_id(db, transaction_id=transaction_id)
    balance_in = crud.balance.get_by_user_id(db, user_id=tr_event_in.user_id, with_lock=True)
    balance_out = crud.balance.update(db,
                                      db_obj=balance_in,
                                      obj_in={"amount": balance_in.amount + tr_event_in.amount}
                                      )
    crud.transaction_balance.create(db,
                                    obj_in=schemas.TransactionBalanceCreate(
                                        transaction_id=transaction_id,
                                        balance_id=balance_out.id,
                                    ))
    return balance_out, tr_event_in
