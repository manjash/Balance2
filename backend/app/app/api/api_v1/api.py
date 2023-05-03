from fastapi import APIRouter

from app.api.api_v1.endpoints import balance, login, order, proxy, service_product, transaction, users

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(proxy.router, prefix="/proxy", tags=["proxy"])
api_router.include_router(balance.router, prefix="/balance", tags=["balance"])
api_router.include_router(transaction.router, prefix="/transaction", tags=["transaction"])
api_router.include_router(service_product.router, prefix="/service_product", tags=["service_product"])
api_router.include_router(order.router, prefix="/order", tags=["order"])
