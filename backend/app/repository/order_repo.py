from app.core.pagination.filters.order import OrderFilter
from app.core.pagination.result import PaginatedResult
from app.core.pagination import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem
from app.schemas.order import OrderResponse
from app.repository.product_repo  import ProductRepository
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        order_in,
        user_id: int,
        total_amount,
        coupon_id: int = None,
        coupon_discount: Decimal = Decimal("0"),
    ) -> Order:
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="pending",
            address=order_in.address,
            coupon_id=coupon_id,
            coupon_discount=coupon_discount,
        )
        self.db.add(order)
        await self.db.flush()  # 获取 order.id

        for item in order_in.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name="",   # 后续在 Service 层填充
                price=0,           # 后续在 Service 层填充
                quantity=item.quantity,
            )
            self.db.add(order_item)

        await self.db.commit()
        # 需要重新查询以 eager load items，否则序列化时报 MissingGreenlet
        order = await self.get_by_id(order.id)
        return order

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id).options(
                selectinload(Order.items),
                selectinload(Order.coupon),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 20, status: str = None) -> PaginatedResult[Order]:
        filters = OrderFilter(
            user_id=user_id,
            status=status if status else None,
        )
        return await paginate(self.db, Order, filters, skip=skip, limit=limit)

    async def get_order_items(self, order_id: int) -> List[OrderItem]:
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        
        return list(result.scalars().all())

    async def get_expired_pending_orders(self, expire_time: datetime) -> List[Order]:
        result = await self.db.execute(
            select(Order).where(
                Order.status == "pending",
                Order.created_at < expire_time
            )
        )
        return list(result.scalars().all())

    async def get_all_orders(self, skip: int = 0, limit: int = 100, status: str = None) -> PaginatedResult[Order]:
        filters = OrderFilter(
            status=status if status else None,
        )
        return await paginate(self.db, Order, filters, skip=skip, limit=limit)

    async def get_all_orders_count(self, status: str = None) -> int:
        query = select(func.count()).select_from(Order)
        if status is not None:
            query = query.where(Order.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update_status(self, order, new_status) -> Order:
        await self.db.execute(
            update(Order).where(Order.id == order.id).values(status=new_status)
        )
        return await self.get_by_id(order.id)
    
    async def get_user_orders_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Order).where(Order.user_id == user_id)
        )
        return result.scalar_one()

    async def restore_stock(self, order_id: int):
        """根据订单 items 回补库存"""
        items = await self.get_order_items(order_id)
        product_repo = ProductRepository(self.db)
        for item in items:
            await product_repo.increase_stock(item.product_id, item.quantity)
