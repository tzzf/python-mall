from app.core.pagination.filters.coupon import CouponFilter
from app.core.pagination import paginate
from app.core.pagination.result import PaginatedResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.coupon import Coupon, UserCoupon
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import joinedload


class CouponRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # === Coupon 表操作 ===

    async def create(self, coupon_in: dict) -> Coupon:
        coupon = Coupon(**coupon_in)
        self.db.add(coupon)
        await self.db.flush()
        await self.db.refresh(coupon)
        return coupon

    async def get_by_id(self, coupon_id: int) -> Optional[Coupon]:
        result = await self.db.execute(
            select(Coupon).where(Coupon.id == coupon_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Coupon]:
        result = await self.db.execute(
            select(Coupon).where(Coupon.code == code)
        )
        return result.scalar_one_or_none()

    async def get_active_list(self) -> List[Coupon]:
        now = datetime.now()
        result = await self.db.execute(
            select(Coupon)
            .where(Coupon.is_active == True)
            .where(Coupon.start_time <= now)
            .where(Coupon.end_time >= now)
            .where(Coupon.remain_count > 0)
            .order_by(Coupon.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, coupon_id: int, **kwargs) -> Optional[Coupon]:
        await self.db.execute(
            update(Coupon).where(Coupon.id == coupon_id).values(**kwargs)
        )
        await self.db.flush()
        return await self.get_by_id(coupon_id)

    async def decrease_stock(self, coupon_id: int) -> bool:
        """扣减库存，返回是否成功"""
        result = await self.db.execute(
            update(Coupon)
            .where(Coupon.id == coupon_id)
            .where(Coupon.remain_count > 0)
            .values(remain_count=Coupon.remain_count - 1)
        )
        await self.db.flush()
        return result.rowcount > 0

    # === UserCoupon 表操作 ===

    async def receive_coupon(self, user_id: int, coupon_id: int) -> UserCoupon:
        """用户领取优惠券"""
        user_coupon = UserCoupon(
            user_id=user_id,
            coupon_id=coupon_id,
            status="unused",
        )
        self.db.add(user_coupon)
        await self.db.flush()
        await self.db.refresh(user_coupon)
        return user_coupon
    
    async def get_coupon_list(self, skip: int = 0, limit: int = 100)-> PaginatedResult[Coupon]:
        filters = CouponFilter(
        )
        return await paginate(self.db, Coupon, filters, skip=skip, limit=limit)

    async def get_user_coupon(self, user_coupon_id: int) -> Optional[UserCoupon]:
        result = await self.db.execute(
            select(UserCoupon)
                .options(joinedload(UserCoupon.coupon))
                .where(UserCoupon.id == user_coupon_id)
        )
        return result.scalar_one_or_none()

    async def get_user_coupons(self, user_id: int, status: str = None) -> List[UserCoupon]:
        query = (
            select(UserCoupon)
                .options(joinedload(UserCoupon.coupon))
                .where(UserCoupon.user_id == user_id)
        )
        if status:
            query = query.where(UserCoupon.status == status)
        result = await self.db.execute(query.order_by(UserCoupon.received_at.desc()))
        return list(result.scalars().all())

    async def use_coupon(self, user_coupon_id: int) -> bool:
        """使用优惠券"""
        result = await self.db.execute(
            update(UserCoupon)
            .where(UserCoupon.id == user_coupon_id)
            .where(UserCoupon.status == "reserved")
            .values(status="used", used_at=datetime.now())
        )
        await self.db.flush()
        return result.rowcount > 0

    async def check_user_received(self, user_id: int, coupon_id: int) -> bool:
        """检查用户是否已领取过"""
        result = await self.db.execute(
            select(UserCoupon).where(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def reserve_coupon(self, user_coupon_id: int, order_id: int) -> bool:
        """预留优惠券给某个订单"""
        result = await self.db.execute(
            update(UserCoupon)
            .where(UserCoupon.id == user_coupon_id)
            .where(UserCoupon.status == "unused")
            .values(status="reserved", reserved_order_id=order_id)
        )
        await self.db.flush()
        return result.rowcount > 0


    async def release_coupon(self, user_coupon_id: int) -> bool:
        """释放预留的优惠券（订单超时取消时调用）"""
        result = await self.db.execute(
            update(UserCoupon)
            .where(UserCoupon.id == user_coupon_id)
            .where(UserCoupon.status == "reserved")
            .values(status="unused", reserved_order_id=None)
        )
        await self.db.flush()
        return result.rowcount > 0


    async def confirm_coupon_use(self, user_coupon_id: int) -> bool:
        """确认使用优惠券（支付成功后调用）"""
        result = await self.db.execute(
            update(UserCoupon)
            .where(UserCoupon.id == user_coupon_id)
            .where(UserCoupon.status == "reserved")
            .values(status="used", used_at=datetime.now())
        )
        await self.db.flush()
        return result.rowcount > 0
