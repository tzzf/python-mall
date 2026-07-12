from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_admin
from app.service.coupon_service import CouponService
from app.repository.coupon_repo import CouponRepository
from app.core.database import get_db
from app.schemas.coupon import CouponCreate, CouponUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/coupons", tags=["管理端-优惠券"])


def get_coupon_service(db: AsyncSession = Depends(get_db)):
    coupon_repo = CouponRepository(db)
    return CouponService(db, coupon_repo)


@router.post("/")
async def create_coupon(
    coupon_in: CouponCreate,
    current_user=Depends(get_current_admin),
    svc: CouponService = Depends(get_coupon_service),
):
    """创建优惠券"""
    try:
        coupon = await svc.create_coupon(coupon_in)
        return coupon
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_admin_coupon_list(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_admin),
    svc: CouponService = Depends(get_coupon_service),
):
    """获取优惠券列表（管理端）"""
    return await svc.get_admin_coupon_list(skip=skip, limit=limit)


@router.patch("/{coupon_id}")
async def update_coupon(
    coupon_id: int,
    coupon_in: CouponUpdate,
    current_user=Depends(get_current_admin),
    svc: CouponService = Depends(get_coupon_service),
):
    """更新优惠券"""
    return await svc.update_coupon(coupon_id, coupon_in.model_dump(exclude_none=True))
