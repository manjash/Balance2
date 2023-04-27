import random
from typing import Tuple, Optional, List

from fastapi.testclient import TestClient
from fastapi import Body
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import TransactionEvent, Transaction, Order, OrderServiceProducts
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string, random_service_product


def random_transaction_and_tr_event(
        client: TestClient,
        db: Session,
        user_id: Optional[str] = Body(None),
        amount=round(random.uniform(1., 1000.), 2),
) -> Tuple[Transaction, TransactionEvent]:
    if not user_id:
        user = create_random_user(db)
        user_id = str(user.id)
    data = {
        "gateway": random_lower_string(),
        "method": random_lower_string(),
        "description": random_lower_string(),
        "data": {},
        "type": random_lower_string(),
        "amount": amount,
        "currency":  random_lower_string()[:3],
        "category":  random_lower_string(),
        "user_id": user_id,
        "gateway_id": random_lower_string()
    }
    r = client.post(f"{settings.API_V1_STR}/transaction/", json=data)
    transaction, t_event = r.json()
    db_transaction = crud.transaction.get_by_id(db, transaction_id=transaction["id"])
    db_transaction_event = crud.transaction_event.get_by_id(db, transaction_event_id=t_event["id"])
    return db_transaction, db_transaction_event


def random_order_service_products(client: TestClient,
                                  db: Session,
                                  transaction_id: str,
                                  ) -> Tuple[Order, List[OrderServiceProducts]]:
    service_products = {}
    for i in range(3):
        sp = random_service_product(client)
        service_products[sp["id"]] = sp["price"]
    return random_order(client, db, service_products=service_products, transaction_id=transaction_id)


def random_order(client: TestClient,
                 db: Session,
                 service_products: dict,
                 transaction_id: str,
                 ) -> Tuple[Order, List[OrderServiceProducts]]:
    # fyi service_products = {service_product_id: price, ...}
    amount = sum(service_products.values())

    data = {
        "transaction_id": str(transaction_id),
        "amount": amount,
        "service_product_price_ids": service_products
    }

    r = client.post(f"{settings.API_V1_STR}/order/", json=data)
    order, all_osp_links = r.json()
    all_osp_links_sp_ids = [a["service_product_id"] for a in all_osp_links]

    order = crud.order.get_by_id(db, order_id=order["id"])
    order_service_products_link = [crud.order_service_products.get_by_order_id_sp_id(
                    db,
                    order_id=order.id,
                    service_product_id=sp_id
                )
                    for sp_id in all_osp_links_sp_ids
                ]
    return order, order_service_products_link
