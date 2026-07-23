from fastapi import APIRouter
from app.api.v1 import users, cart, order, pay, coupon, products, channel

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(cart.router)
api_router.include_router(order.router)
api_router.include_router(pay.router)
api_router.include_router(coupon.router)
api_router.include_router(products.router)
api_router.include_router(channel.router)

