from fastapi import APIRouter, Depends, HTTPException
from app.core.redis import get_redis
from app.api.deps import get_current_v1_user
from app.repository.cart_repo import CartRepository
from app.repository.product_repo import ProductRepository
from app.service.cart_service import CartService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartResponse
from typing import List
import redis.asyncio as redis

router = APIRouter(prefix="/cart", tags=["用户端-购物车"])

def get_cart_service(
    redis_client: redis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    cart_repo = CartRepository(redis_client)
    product_repo = ProductRepository(db)
    return CartService(cart_repo, product_repo)


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user=Depends(get_current_v1_user),
    svc: CartService = Depends(get_cart_service),
):
    return await svc.get_cart(current_user.id)


@router.post("/items")
async def add_cart_item(
    item: CartItemAdd,
    current_user=Depends(get_current_v1_user),
    svc: CartService = Depends(get_cart_service),
):
    try:
        return await svc.add_item(current_user.id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/items/{product_id}")
async def update_cart_item(
    product_id: int,
    item: CartItemUpdate,
    current_user=Depends(get_current_v1_user),
    svc: CartService = Depends(get_cart_service),
):
    try:
        return await svc.update_item(current_user.id, product_id, item.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{product_id}")
async def remove_cart_item(
    product_id: int,
    current_user=Depends(get_current_v1_user),
    svc: CartService = Depends(get_cart_service),
):
    return await svc.remove_item(current_user.id, product_id)


@router.delete("/")
async def clear_cart(
    current_user=Depends(get_current_v1_user),
    svc: CartService = Depends(get_cart_service),
):
    return await svc.clear_cart(current_user.id)
