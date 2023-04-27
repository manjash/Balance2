import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.tests.utils.utils import random_lower_string


def test_create(client: TestClient, db: Session):
    data = {
        "title": random_lower_string(),
        "description": random_lower_string(),
        "price": round(random.uniform(1., 1000.), 2),
        "unit": random_lower_string()
    }

    r = client.post(
        f"{settings.API_V1_STR}/service_product/", json=data,
    )
    assert 200 == r.status_code
    api_service_product = r.json()
    existing_sp = crud.service_product.get_by_id(db, service_product_id=api_service_product["id"])
    assert existing_sp
    assert existing_sp.title == data["title"]
    assert existing_sp.description == data["description"]
    assert existing_sp.price == data["price"]
    assert existing_sp.unit == data["unit"]
