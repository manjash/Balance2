import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.balance import BalanceCreate
from app.models.balance import Balance
from app.tests.utils.utils import random_lower_string
from app.tests.utils.user import \
    create_random_user, \
    create_random_user_with_balance
from app.tests.utils.balance import arrange_for_balance_reserve
from uuid import UUID


def test_create_balance_zero(
        client: TestClient, db: Session):
    # valid user_id and invalid user_id
    user = create_random_user(db)
    data = {"user_id": str(user.id)}
    r = client.post(
        f"{settings.API_V1_STR}/balance/", json=data,
    )
    api_balance = r.json()
    assert 200 == r.status_code
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    assert db_balance
    assert db_balance.user_id == UUID(api_balance["user_id"])
    assert db_balance.amount == api_balance["amount"]
    assert db_balance.amount == 0.
    assert db_balance.amount_reserved == 0.


def test_create_balance_non_zero(
        client: TestClient, db: Session):
    # valid user_id and invalid user_id
    user = create_random_user(db)
    amount = round(random.uniform(1., 1000.), 2)
    data = {
        "user_id": str(user.id),
        "amount": amount
    }
    r = client.post(
        f"{settings.API_V1_STR}/balance/", json=data,
    )
    api_balance = r.json()
    assert 200 == r.status_code
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    assert db_balance
    assert db_balance.user_id == UUID(api_balance["user_id"])
    assert db_balance.amount == api_balance["amount"] == amount
    assert db_balance.amount_reserved == 0.


def test_create_balance_existing_user(
        client: TestClient, db: Session):
    # valid user_id and invalid user_id
    user, balance = create_random_user_with_balance(db, amount=0)
    data = {"user_id": str(user.id)}
    r = client.post(
        f"{settings.API_V1_STR}/balance/", json=data,
    )
    api_response = r.json()
    assert 400 == r.status_code
    assert "already registered" in api_response["detail"]
    users_with_user_id = db.query(Balance).filter(Balance.user_id == user.id).all()
    assert len(users_with_user_id) == 1


def test_get_balance_by_user_id(
        client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    user, balance = create_random_user_with_balance(db, amount=amount)

    r = client.get(
        f"{settings.API_V1_STR}/balance/getBalance/{str(user.id)}",
    )
    api_balance = r.json()
    assert 200 == r.status_code
    assert api_balance
    assert UUID(api_balance["user_id"]) == balance.user_id
    assert api_balance["amount"] == balance.amount
    assert balance.amount == amount
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    assert db_balance.amount == amount
    assert db_balance.amount_reserved == 0.
    assert db_balance.user_id == user.id


def test_balance_to_balance_transaction_enough_funds(
        client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    amount_to_transfer = round(amount / 2.3, 2)

    user = create_random_user(db)
    user2 = create_random_user(db)

    # Test case when sender doesn't have a balance account
    data = {"from_user_id": str(user.id), "to_user_id": str(user2.id), "amount": amount_to_transfer}
    r = client.post(
        f"{settings.API_V1_STR}/balance/internalTransfer", json=data,
    )
    assert 400 == r.status_code
    assert "The user doesn't have a balance account" in r.json()["detail"]

    balance_in = BalanceCreate(user_id=str(user.id), amount=amount)
    balance = crud.balance.create(db, obj_in=balance_in)
    assert balance.amount == amount

    # Test case when receiver doesn't have a balance account
    data = {"from_user_id": str(user.id), "to_user_id": str(user2.id), "amount": amount_to_transfer}
    r = client.post(
        f"{settings.API_V1_STR}/balance/internalTransfer", json=data,
    )
    assert 400 == r.status_code
    assert "The user doesn't have a balance account" in r.json()["detail"]

    # Test case when both accounts exist
    balance_in2 = BalanceCreate(user_id=str(user2.id), amount=0)
    balance2 = crud.balance.create(db, obj_in=balance_in2)
    assert balance2.amount == 0

    data = {"from_user_id": str(user.id), "to_user_id": str(user2.id), "amount": amount_to_transfer}
    r = client.post(
        f"{settings.API_V1_STR}/balance/internalTransfer", json=data,
    )
    balance_from, balance_to = r.json()
    assert 200 == r.status_code
    assert balance_from["amount"] == amount - amount_to_transfer
    assert balance_to["amount"] == amount_to_transfer
    assert UUID(balance_from["user_id"]) == user.id
    assert UUID(balance_to["user_id"]) == user2.id
    crud.balance.close_session(db)
    db_balance_from = crud.balance.get_by_user_id(db, user_id=user.id)
    db_balance_to = crud.balance.get_by_user_id(db, user_id=user2.id)
    assert db_balance_from.amount == amount - amount_to_transfer
    assert db_balance_to.amount == amount_to_transfer
    assert db_balance_from.amount_reserved == 0.
    assert db_balance_to.amount_reserved == 0.


def test_balance_to_balance_transaction_not_enough_funds(
        client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    amount_to_transfer = round(amount * 2.33, 2)

    user, balance = create_random_user_with_balance(db, amount=amount)
    assert balance.amount == amount

    user2, balance2 = create_random_user_with_balance(db, amount=0)
    assert balance2.amount == 0

    data = {
        "from_user_id": str(user.id),
        "to_user_id": str(user2.id),
        "amount": amount_to_transfer
    }
    r = client.post(
        f"{settings.API_V1_STR}/balance/internalTransfer", json=data,
    )
    assert 400 == r.status_code
    assert "Not enough funds" in r.json()["detail"]
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    assert db_balance.amount == amount
    assert db_balance.amount_reserved == 0.
    db_balance_2 = crud.balance.get_by_user_id(db, user_id=user2.id)
    assert db_balance_2.amount == 0.
    assert db_balance_2.amount_reserved == 0.


def test_add_to_balance(client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    user, balance = create_random_user_with_balance(db, amount=amount)
    amount_to_add = round(random.uniform(1., 1000.), 2)
    data = {
        "user_id": str(user.id),
        "amount": amount_to_add
    }
    r = client.post(
        f"{settings.API_V1_STR}/balance/moneyIn", json=data,
    )
    crud.balance.close_session(db)
    assert 200 == r.status_code
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)

    assert r.json()["amount"] == db_balance.amount == sum([amount, amount_to_add])
    assert UUID(r.json()["user_id"]) == db_balance.user_id == user.id


def test_withdraw_from_balance(client: TestClient, db: Session):
    amount = round(random.uniform(1., 1000.), 2)
    user, balance = create_random_user_with_balance(db, amount=amount)
    amount_to_withdraw = round(amount / random.uniform(2., 100.), 2)
    data = {
        "user_id": str(user.id),
        "amount": amount_to_withdraw
    }
    r = client.post(
        f"{settings.API_V1_STR}/balance/moneyOut", json=data,
    )
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    assert 200 == r.status_code

    assert r.json()["amount"] == db_balance.amount == amount - amount_to_withdraw
    assert UUID(r.json()["user_id"]) == db_balance.user_id == user.id

    user2, balance2 = create_random_user_with_balance(db, amount=amount)
    amount_to_withdraw = amount * round(random.uniform(2, 100), 2)
    data = {"user_id": str(user2.id), "amount": amount_to_withdraw}
    r = client.post(
        f"{settings.API_V1_STR}/balance/moneyOut", json=data,
    )
    assert 400 == r.status_code
    assert "Balance can't be updated to negative" in r.json()["detail"]


def test_reserve_enough_funds(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db
    )
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved
    order_id, order_amount = order.id, order.amount

    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve", json=data,
    )  # --> creates TransactionBalance, OrderServiceProduct; returns  Balance
    crud.balance.close_session(db)
    assert 200 == r.status_code
    api_balance = r.json()
    db_balance = crud.balance.get_by_balance_id(db, balance_id=balance.id)
    db_order = crud.order.get_by_id(db, order_id=order_id)
    db_transaction = crud.transaction.get_by_id(db, transaction_id=transaction.id)
    assert db_balance.amount == api_balance["amount"] == initial_amount - sp_price
    assert db_balance.amount_reserved == api_balance["amount_reserved"] == initial_amount_reserved + sp_price
    assert db_order.transaction_id == db_transaction.id

    tr_event_link = crud.transaction_event.get_by_transaction_id(
        db, transaction_id=transaction.id)
    assert tr_event_link
    assert tr_event_link.amount == ospl.price == order_amount == sp_price
    assert tr_event_link.user_id == user.id == tr_event.user_id
    assert ospl.status == "authorised"


def test_reserve_not_enough_funds(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db, multiple_operation="/"
    )
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved

    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve", json=data,
    )
    assert 400 == r.status_code
    api_balance = r.json()
    assert "Balance can't be updated to negative" in api_balance["detail"]

    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    assert db_balance.amount == initial_amount
    assert db_balance.amount_reserved == initial_amount_reserved
    assert db_balance.user_id == user.id


def test_reserve_capture(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db
    )
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved
    order_id = order.id

    assert ospl.price == data["amount"]
    assert ospl.status == "authorised"

    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve/capture", json=data,
    )
    assert 200 == r.status_code
    api_balance, api_osp = r.json()
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user.id)
    db_osp = crud.order_service_products.get_by_order_id_sp_id(
        db,
        order_id=order_id,
        service_product_id=sp_id,
    )
    assert db_balance.amount == api_balance["amount"]
    assert db_balance.amount_reserved == api_balance["amount_reserved"]
    assert db_balance.amount == initial_amount
    assert db_balance.amount_reserved == initial_amount_reserved - data["amount"]
    assert db_osp.order_id == UUID(api_osp["order_id"])
    assert db_osp.status == "captured"


def test_reserve_capture_not_auth(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db
    )
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved
    order_id = order.id
    user_id = user.id

    assert ospl.price == data["amount"]
    assert ospl.status == "authorised"
    random_status = random_lower_string()
    crud.order_service_products.update(db, db_obj=ospl, obj_in={"status": random_status})
    assert ospl.status != "authorised"

    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve/capture", json=data,
    )
    assert 400 == r.status_code
    api_result = r.json()
    assert "The amount is not authorised" == api_result['detail']
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user_id)
    db_osp = crud.order_service_products.get_by_order_id_sp_id(
        db,
        order_id=order_id,
        service_product_id=sp_id,
    )

    assert db_balance.amount == initial_amount
    assert db_balance.amount_reserved == initial_amount_reserved
    assert db_osp.order_id == order_id
    assert db_osp.status == random_status


def test_reserve_refund_authorised(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db
    )
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved
    order_id = order.id
    user_id = user.id
    transaction_id = transaction.id
    assert crud.order_service_products.get_by_id(db, order_service_product_id=ospl.id).status == "authorised"

    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve/refund", json=data,
    )
    assert 200 == r.status_code
    api_balance, api_osp = r.json()
    crud.balance.close_session(db)
    db_balance = crud.balance.get_by_user_id(db, user_id=user_id)
    db_ospl = crud.order_service_products.get_by_order_id_sp_id(db, order_id=order_id, service_product_id=sp_id)
    db_transaction = crud.transaction.get_by_id(db, transaction_id=transaction_id)
    db_tr_event = crud.transaction_event.get_by_transaction_id(db, transaction_id=transaction_id)
    assert api_osp["status"] == db_ospl.status == "refunded"
    assert UUID(api_osp["order_id"]) == db_ospl.order_id == order_id
    assert UUID(api_osp["service_product_id"]) == db_ospl.service_product_id == UUID(sp_id)
    assert api_balance["amount"] == db_balance.amount == initial_amount + sp_price
    assert api_balance["amount_reserved"] == db_balance.amount_reserved == initial_amount_reserved - sp_price
    assert UUID(api_balance["user_id"]) == db_balance.user_id == user_id == db_tr_event.user_id
    assert db_transaction.id == transaction_id == db_tr_event.transaction_id


def test_reserve_refund_captured(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db
    )
    crud.order_service_products.update(db, db_obj=ospl, obj_in={"status": "captured"})
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved
    order_id = order.id
    user_id = user.id
    transaction_id = transaction.id
    assert crud.order_service_products.get_by_id(db, order_service_product_id=ospl.id).status == "captured"
    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve/refund", json=data,
    )
    assert 200 == r.status_code
    api_balance, api_osp = r.json()
    crud.balance.close_session(db)

    db_balance = crud.balance.get_by_user_id(db, user_id=user_id)
    db_ospl = crud.order_service_products.get_by_order_id_sp_id(db, order_id=order_id, service_product_id=sp_id)
    db_transaction = crud.transaction.get_by_id(db, transaction_id=transaction_id)
    db_tr_event = crud.transaction_event.get_by_transaction_id(db, transaction_id=transaction_id)
    assert api_osp["status"] == db_ospl.status == "refunded"
    assert UUID(api_osp["order_id"]) == db_ospl.order_id == order_id
    assert UUID(api_osp["service_product_id"]) == db_ospl.service_product_id == UUID(sp_id)
    assert api_balance["amount"] == db_balance.amount == initial_amount + sp_price
    assert api_balance["amount_reserved"] == db_balance.amount_reserved == initial_amount_reserved
    assert UUID(api_balance["user_id"]) == db_balance.user_id == user_id == db_tr_event.user_id
    assert db_transaction.id == transaction_id == db_tr_event.transaction_id


def test_reserve_refund_other(client: TestClient, db: Session):
    sp_id, sp_price, user, balance, transaction, tr_event, order, ospl, data = arrange_for_balance_reserve(
        client, db
    )
    ospl_status_upd = random_lower_string()
    crud.order_service_products.update(db, db_obj=ospl, obj_in={"status": ospl_status_upd})
    initial_amount, initial_amount_reserved = balance.amount, balance.amount_reserved
    order_id = order.id
    user_id = user.id
    transaction_id = transaction.id
    assert crud.order_service_products.get_by_id(db, order_service_product_id=ospl.id).status == ospl_status_upd
    r = client.post(
        f"{settings.API_V1_STR}/balance/reserve/refund", json=data,
    )
    assert 400 == r.status_code
    api_response = r.json()
    assert "order_service_product.status is incorrect, the balance can't be refunded" in api_response["detail"]
    crud.balance.close_session(db)

    db_balance = crud.balance.get_by_user_id(db, user_id=user_id)
    db_ospl = crud.order_service_products.get_by_order_id_sp_id(db, order_id=order_id, service_product_id=sp_id)
    db_transaction = crud.transaction.get_by_id(db, transaction_id=transaction_id)
    db_tr_event = crud.transaction_event.get_by_transaction_id(db, transaction_id=transaction_id)
    assert db_ospl.status == ospl_status_upd
    assert db_ospl.order_id == order_id
    assert db_ospl.service_product_id == UUID(sp_id)
    assert db_balance.amount == initial_amount
    assert db_balance.amount_reserved == initial_amount_reserved
    assert db_balance.user_id == user_id == db_tr_event.user_id

    assert db_transaction.id == transaction_id == db_tr_event.transaction_id


def test_accountant_report(client: TestClient, db: Session):
    pass
