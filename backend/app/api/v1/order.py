from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import get_redis
from app.api.deps import get_current_v1_user
from app.repository.order_repo import OrderRepository
from app.repository.product_repo import ProductRepository
from app.repository.cart_repo import CartRepository
from app.service.order_service import OrderService
from app.schemas.order import OrderCreate, OrderResponse, PaginatedOrdersResponse, OrderCancelResponse, OrderConfirmReceiptResponse
from typing import List
import redis.asyncio as redis

router = APIRouter(prefix="/orders", tags=["用户端-订单"])


def get_order_service(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    return OrderService(
        db,
        OrderRepository(db),
        ProductRepository(db),
        CartRepository(redis_client),
    )


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_in: OrderCreate,
    current_user=Depends(get_current_v1_user),
    svc: OrderService = Depends(get_order_service),
):
    try:
        order = await svc.create_order(current_user.id, order_in)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedOrdersResponse)
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    current_user=Depends(get_current_v1_user),
    svc: OrderService = Depends(get_order_service),
):
    result = await svc.get_user_orders(current_user.id, skip, limit)
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user=Depends(get_current_v1_user),
    svc: OrderService = Depends(get_order_service),
):
    try:
        result = await svc.get_order_detail(current_user.id, order_id)
        return result["order"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: int,
    current_user=Depends(get_current_v1_user),
    svc: OrderService = Depends(get_order_service),
):
    try:
        order = await svc.cancel_order(current_user.id, order_id)
        return OrderCancelResponse(
            id=order.id,
            status=order.status,
            message="订单已取消，库存已退回"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/confirm-receipt", response_model=OrderConfirmReceiptResponse)
async def confirm_receipt(
    order_id: int,
    current_user=Depends(get_current_v1_user),
    svc: OrderService = Depends(get_order_service),
):
    try:
        order = await svc.confirm_receipt(current_user.id, order_id)
        return OrderConfirmReceiptResponse(
            id=order.id,
            status=order.status,
            message="确认收货成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
