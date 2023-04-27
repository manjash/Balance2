import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.tests.utils.utils import random_service_product
from app.tests.utils.user import create_random_user_with_balance
from uuid import UUID
from app.tests.utils.transaction import random_transaction_and_tr_event


def test_create_single(client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    transaction, tr_event = random_transaction_and_tr_event(client, db, amount=amount, user_id=None)
    service_product = random_service_product(client)
    service_product_price_ids = {service_product["id"]: service_product["price"]}
    data = {
        "transaction_id": str(transaction.id),
        "amount": amount,
        "service_product_price_ids": service_product_price_ids
    }
    r = client.post(f"{settings.API_V1_STR}/order/", json=data)
    api_order, api_osps = r.json()
    db_order = crud.order.get_by_id(db, order_id=api_order["id"])
    db_osps = crud.order_service_products.get_by_order_id_sp_id(
        db, order_id=api_order["id"], service_product_id=api_osps[0]["service_product_id"]
    )
    assert db_order
    assert db_order.transaction_id == UUID(api_order["transaction_id"])
    assert db_order.transaction_id == transaction.id
    assert db_order.amount == api_order["amount"]
    assert db_order.status == "pending"
    assert transaction.id == tr_event.transaction_id

    assert db_osps
    assert db_osps.price == api_osps[0]["price"]
    assert db_osps.price == service_product["price"]
    assert db_osps.status == "authorised"
    assert db_osps.order_id == db_order.id


def test_create_multi(client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    transaction, tr_event = random_transaction_and_tr_event(client, db, amount=amount, user_id=None)
    sp_num = 4
    service_products = [random_service_product(client) for i in range(sp_num)]
    service_product_price_ids = {service_products[i]["id"]: service_products[i]["price"] for i in range(sp_num)}
    data = {
        "transaction_id": str(transaction.id),
        "amount": amount,
        "service_product_price_ids": service_product_price_ids
    }
    r = client.post(f"{settings.API_V1_STR}/order/", json=data)
    api_order, api_osps = r.json()
    db_order = crud.order.get_by_id(db, order_id=api_order["id"])
    db_osps = [crud.order_service_products.get_by_order_id_sp_id(db,
                                                                 order_id=api_order["id"],
                                                                 service_product_id=api_osps[i]["service_product_id"]
                                                                 ) for i in range(sp_num)]
    assert db_order
    assert db_order.transaction_id == UUID(api_order["transaction_id"])
    assert db_order.amount == api_order["amount"]
    assert db_order.status == "pending"

    assert db_osps
    db_osps_sorted = sorted([(db_osps[i].service_product_id, db_osps[i].order_id, db_osps[i].price)
                             for i in range(sp_num)], key=lambda x: x[0])
    api_osps_sorted = sorted([(UUID(api_osps[i]["service_product_id"]),
                               UUID(api_osps[i]["order_id"]),
                               api_osps[i]["price"]
                               ) for i in range(sp_num)
                              ],
                             key=lambda x: x[0])
    service_products_sorted = sorted([(UUID(service_products[i]["id"]),
                                       UUID(api_order["id"]),
                                       service_products[i]["price"]
                                       ) for i in range(sp_num)
                                      ],
                                     key=lambda x: x[0])
    assert db_osps_sorted == api_osps_sorted
    assert db_osps_sorted == service_products_sorted

    for i in range(len(api_osps)):
        assert db_osps[i].status == "authorised"
        assert api_osps[i]["status"] == "authorised"


def test_captured_money_to_balance(client: TestClient, db: Session):
    user, balance = create_random_user_with_balance(db)
    amount = round(random.uniform(1., 1000.), 2)
    transaction, tr_event = random_transaction_and_tr_event(client, db, amount=amount, user_id=str(user.id))

    data = str(transaction.id)
    r = client.post(f"{settings.API_V1_STR}/order/captured_to_balance", json=data)
    crud.order.close_session(db)
    api_balance, api_tr_event = r.json()

    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    db_transaction = crud.transaction.get_by_id(db, transaction_id=transaction.id)
    db_tr_event = crud.transaction_event.get_by_transaction_id(db, transaction_id=transaction.id)
    db_tr_balance = crud.transaction_balance.get_by_transaction_id(db, transaction_id=transaction.id)

    assert api_balance
    assert api_balance["amount"] == db_balance.amount
    assert db_balance.amount == balance.amount + amount
    assert db_balance.amount_reserved == balance.amount_reserved
    assert db_balance.user_id == user.id

    assert db_tr_balance
    assert db_tr_balance.balance_id == balance.id
    assert db_tr_balance.transaction_id == transaction.id
    assert db_tr_balance.balance_id == UUID(api_balance["id"])
    assert db_tr_balance.transaction_id == UUID(api_tr_event["transaction_id"])

    assert api_tr_event
    assert db_tr_event
    assert db_transaction
    assert db_tr_event.amount == amount
    assert api_tr_event["amount"] == amount
    assert db_tr_event.transaction_id == UUID(api_tr_event["transaction_id"])
    assert db_tr_event.user_id == UUID(api_tr_event["user_id"])
    assert db_tr_event.transaction_id == transaction.id
    assert db_tr_event.user_id == user.id
