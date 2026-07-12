from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.repository.order_repo import OrderRepository
from app.service.order_service import OrderService
from app.schemas.order import OrderStatusUpdate, PaginatedOrdersResponse
from typing import List, Optional

router = APIRouter(prefix="/orders", tags=["管理端-订单"])

def get_order_service(db: AsyncSession = Depends(get_db)):
    return OrderService(db, OrderRepository(db), None, None)


@router.get("/", response_model=PaginatedOrdersResponse)
async def list_all_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    current_admin=Depends(get_current_admin),
    svc: OrderService = Depends(get_order_service),
):
    return await svc.get_all_orders(skip=skip, limit=limit, status=status)


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    current_admin=Depends(get_current_admin),
    svc: OrderService = Depends(get_order_service),
):
    try:
        order = await svc.update_order_status(order_id, status_in.status.value)
        return {"message": "状态更新成功", "status": order.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
