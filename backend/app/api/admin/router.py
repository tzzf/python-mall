from fastapi import APIRouter
from app.api.admin import users, products, order, coupon

admin_router = APIRouter()
admin_router.include_router(users.router)
admin_router.include_router(products.router)
admin_router.include_router(order.router)
admin_router.include_router(coupon.router)
