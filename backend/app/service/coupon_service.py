from app.repository.coupon_repo import CouponRepository
from app.schemas.coupon import (
    CouponInfo,
    CouponCreate,          # 新增
    UserCouponDetail,
    ReceiveCouponResponse,
    DiscountCalculateResponse,
    UseCouponResponse,
    UpdateCouponResponse,
)
from decimal import Decimal
from datetime import datetime
from app.models.coupon import Coupon
from typing import Optional, List
from sqlalchemy import select, func
import json


class CouponService:
    def __init__(self, db, coupon_repo: CouponRepository):
        self.db = db
        self.coupon_repo = coupon_repo

    async def create_coupon(self, coupon_in: CouponCreate) -> CouponInfo:
        """管理员创建优惠券"""
        existing = await self.coupon_repo.get_by_code(coupon_in.code)
        if existing:
            raise ValueError(f"优惠券码 {coupon_in.code} 已存在")

        coupon = await self.coupon_repo.create(coupon_in.model_dump())
        await self.db.commit()
        return CouponInfo.model_validate(coupon)

    async def get_coupon_list(self) -> List[CouponInfo]:
        """获取优惠券列表（用户端：有效的）"""
        result = await self.db.execute(
            select(Coupon)
            .order_by(Coupon.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_admin_coupon_list(self, skip: int = 0, limit: int = 100):
        return await self.coupon_repo.get_coupon_list(skip=skip,limit=limit)

    async def receive_coupon(self, user_id: int, coupon_id: int) -> ReceiveCouponResponse:
        coupon = await self.coupon_repo.get_by_id(coupon_id)
        if not coupon:
            raise ValueError("优惠券不存在")

        if await self.coupon_repo.check_user_received(user_id, coupon_id):
            raise ValueError("您已领取过该优惠券")

        if coupon.remain_count <= 0:
            raise ValueError("优惠券已领完")

        now = datetime.now()
        if now < coupon.start_time:
            raise ValueError("优惠券还未开始")
        if now > coupon.end_time:
            raise ValueError("优惠券已过期")

        success = await self.coupon_repo.decrease_stock(coupon_id)
        if not success:
            raise ValueError("优惠券库存扣减失败")

        user_coupon = await self.coupon_repo.receive_coupon(user_id, coupon_id)
        await self.db.commit()
        return ReceiveCouponResponse(
            id=user_coupon.id,
            coupon_id=coupon_id,
            code=coupon.code,
            name=coupon.name,
            message="领取成功",
        )

    async def get_user_coupons(self, user_id: int, status: str = None) -> List[UserCouponDetail]:
        user_coupons = await self.coupon_repo.get_user_coupons(user_id, status)
        result = []
        for uc in user_coupons:
            coupon = uc.coupon
            now = datetime.now()
            final_status = uc.status
            if final_status == "unused" and now > coupon.end_time:
                final_status = "expired"

            result.append(UserCouponDetail(
                id=uc.id,
                coupon_id=coupon.id,
                code=coupon.code,
                name=coupon.name,
                discount_type=coupon.discount_type,
                discount_value=coupon.discount_value,
                status=final_status,
                received_at=uc.received_at,
            ))
        return result

    async def calculate_discount(self, user_coupon_id: int, order_amount: Decimal) -> DiscountCalculateResponse:
        user_coupon = await self.coupon_repo.get_user_coupon(user_coupon_id)
        if not user_coupon:
            raise ValueError("用户优惠券不存在")

        coupon = user_coupon.coupon

        if user_coupon.status != "unused":
            raise ValueError("优惠券已使用或已过期")

        if order_amount < coupon.min_order_amount:
            raise ValueError(f"订单金额不足，最低需 {coupon.min_order_amount} 元")

        if coupon.discount_type == "fixed":
            discount = min(coupon.discount_value, order_amount)
        else:
            discount = order_amount * (coupon.discount_value / 100)
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)

        discount = min(discount, order_amount)
        final_amount = order_amount - discount

        return DiscountCalculateResponse(
            original_amount=str(order_amount),
            discount_amount=str(discount),
            final_amount=str(final_amount),
            coupon_code=coupon.code,
        )

    async def use_coupon(self, user_coupon_id: int, order_id: int) -> UseCouponResponse:
        success = await self.coupon_repo.use_coupon(user_coupon_id)
        if not success:
            raise ValueError("优惠券使用失败，可能已使用或已过期")
        return UseCouponResponse(message="优惠券使用成功", order_id=order_id)

    async def update_coupon(self, coupon_id: int, coupon_in: dict) -> UpdateCouponResponse:
        coupon = await self.coupon_repo.update(coupon_id, **coupon_in)
        if not coupon:
            raise ValueError("优惠券不存在")
        await self.db.commit()
        return UpdateCouponResponse.model_validate(coupon)
