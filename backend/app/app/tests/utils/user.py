from typing import Dict, Tuple

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models.user import User
from app.models.balance import Balance
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.balance import BalanceCreate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/oauth", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(username=email, email=email, password=password)
    user = crud.user.create(db=db, obj_in=user_in)
    return user


def create_random_user_with_balance(db: Session, amount=0) -> Tuple[User, Balance]:
    user = create_random_user(db)
    balance_in = BalanceCreate(user_id=str(user.id), amount=amount)
    balance = crud.balance.create(db, obj_in=balance_in)
    return user, balance


def create_random_user_with_balance_reserve(
        db: Session,
        amount=0.,
        amount_reserved=0.,
) -> Tuple[User, Balance]:
    user = create_random_user(db)
    balance_in = BalanceCreate(
        user_id=str(user.id),
        amount=amount,
    )
    balance = crud.balance.create(db, obj_in=balance_in)
    balance = crud.balance\
        .update(db,
                db_obj=balance,
                obj_in={"amount_reserved": amount_reserved}
                )
    return user, balance


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(username=email, email=email, password=password)
        user = crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
