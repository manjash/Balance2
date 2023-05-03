from .crud_balance import balance  # noqa: F401
from .crud_order import order  # noqa: F401
from .crud_order_service_products import order_service_products  # noqa: F401
from .crud_service_product import service_product  # noqa: F401
from .crud_token import token  # noqa: F401
from .crud_transaction import transaction  # noqa: F401
from .crud_transaction_balance import transaction_balance  # noqa: F401
from .crud_transaction_event import transaction_event  # noqa: F401
from .crud_user import user  # noqa: F401

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
