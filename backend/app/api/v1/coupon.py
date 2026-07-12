from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_v1_user
from app.service.coupon_service import CouponService
from app.repository.coupon_repo import CouponRepository
from app.core.database import get_db
from decimal import Decimal
from app.schemas.coupon import (
    ReceiveCouponRequest,
    UseCouponRequest,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/coupons", tags=["用户端-优惠券"])


def get_coupon_service(db: AsyncSession = Depends(get_db)):
    coupon_repo = CouponRepository(db)
    return CouponService(db, coupon_repo)


@router.get("/")
async def get_coupon_list(svc: CouponService = Depends(get_coupon_service)):
    """获取可用优惠券列表"""
    return await svc.get_coupon_list()


@router.post("/receive")
async def receive_coupon(
    req: ReceiveCouponRequest,
    current_user=Depends(get_current_v1_user),
    svc: CouponService = Depends(get_coupon_service),
):
    """领取优惠券"""
    try:
        result = await svc.receive_coupon(current_user.id, req.coupon_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my")
async def get_my_coupons(
    status: str = None,
    current_user=Depends(get_current_v1_user),
    svc: CouponService = Depends(get_coupon_service),
):
    """获取我的优惠券"""
    return await svc.get_user_coupons(current_user.id, status)


@router.get("/calculate")
async def calculate_discount(
    user_coupon_id: int,
    order_amount: float,
    current_user=Depends(get_current_v1_user),
    svc: CouponService = Depends(get_coupon_service),
):
    """计算折扣金额（下单前预览）"""
    try:
        result = await svc.calculate_discount(user_coupon_id, Decimal(str(order_amount)))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
