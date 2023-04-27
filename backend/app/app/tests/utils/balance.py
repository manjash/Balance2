import random

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.tests.utils.utils import random_service_product
from app.tests.utils.transaction import random_order, random_transaction_and_tr_event
from app.tests.utils.user import create_random_user_with_balance_reserve


def arrange_for_balance_reserve(client: TestClient, db: Session, multiple_operation="*"):
    service_product = random_service_product(client)
    sp_id, sp_price = service_product["id"], service_product["price"]
    service_product = {sp_id: sp_price}

    balance_amount = round(sp_price * random.uniform(2., 4.), 2)
    if multiple_operation == "/":
        balance_amount = round(sp_price / random.uniform(2., 4.), 2)

    user, balance = create_random_user_with_balance_reserve(
        db,
        amount=balance_amount,
        amount_reserved=sp_price,
    )

    transaction, tr_event = random_transaction_and_tr_event(client, db, user_id=str(user.id), amount=sp_price)

    # order w/1 service_product
    order, ospl = random_order(client, db, service_products=service_product, transaction_id=str(transaction.id))
    ospl = ospl[0]
    order_id = order.id

    data = {
        "user_id": str(user.id),
        "service_product_id": str(sp_id),
        "order_id": str(order_id),
        "amount": sp_price
    }
    return sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data
