from app.repository.order_repo import OrderRepository
from app.repository.product_repo import ProductRepository
from app.repository.cart_repo import CartRepository
from app.schemas.order import OrderCreate, OrderStatus
from app.service.coupon_service import CouponService
from app.models.order import Order
from decimal import Decimal
from typing import List
from app.core.redis import get_redis
from app.core.aspects import observe_order_status_change
from datetime import datetime, timedelta

class OrderService:
    def __init__(self, db, order_repo: OrderRepository, product_repo: ProductRepository, cart_repo: CartRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.cart_repo = cart_repo
        self.db = db

    async def create_order(self, user_id: int, order_in: OrderCreate) -> Order:
        # 1. 校验每个商品的库存，并计算总价
        total_amount = Decimal("0")
        product_infos = []

        for item in order_in.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise ValueError(f"商品 ID {item.product_id} 不存在")
            if product.stock < item.quantity:
                raise ValueError(f"商品「{product.name}」库存不足，当前库存: {product.stock}")

            total_amount += product.price * item.quantity
            product_infos.append({
                "product": product,
                "quantity": item.quantity,
                "product_id": item.product_id,
            })
        
        # 2. 处理优惠券预留
        coupon_id = None
        coupon_discount = Decimal("0")
        reserved_user_coupon_id = None  # 记录下来，用于后续预留

        if order_in.coupon_code:
            from app.repository.coupon_repo import CouponRepository
            coupon_repo = CouponRepository(self.db)

            # 2.1 通过 coupon_code 找到 Coupon
            coupon = await coupon_repo.get_by_code(order_in.coupon_code)
            if not coupon:
                raise ValueError("优惠券不存在")

            # 2.2 查询用户已领取且未使用的券
            user_coupons = await coupon_repo.get_user_coupons(user_id, status="unused")
            user_coupon = next(
                (uc for uc in user_coupons if uc.coupon_id == coupon.id),
                None
            )
            if not user_coupon:
                raise ValueError("您尚未领取该优惠券或已使用")

            # 2.3 计算折扣
            discount_result = await CouponService(self.db, coupon_repo).calculate_discount(
                user_coupon.id, total_amount
            )
            coupon_discount = Decimal(discount_result.discount_amount)
            coupon_id = coupon.id
            reserved_user_coupon_id = user_coupon.id  # 先记下来，订单创建完再预留

        # 3. 扣减库存
        for info in product_infos:
            await self.product_repo.reduce_stock(
                info["product"].id,
                info["quantity"]
            )

        # 4. 创建订单
        final_amount = total_amount - coupon_discount
        order = await self.order_repo.create_order(
            order_in, user_id, final_amount,
            coupon_id=coupon_id,
            coupon_discount=coupon_discount
        )

        # 5. 填充 OrderItem 的 product_name 和 price
        from sqlalchemy import select
        from app.models.order import OrderItem
        for item in order_in.items:
            info = next((info for info in product_infos if info['product_id'] == item.product_id), None)
            if info:
                product = info["product"]
                result = await self.db.execute(
                    select(OrderItem).where(
                        OrderItem.order_id == order.id,
                        OrderItem.product_id == item.product_id
                    )
                )
                oi = result.scalar_one()
                oi.product_name = product.name
                oi.price = product.price
        

        # === 6. 预留优惠券（此时才有 order.id）===
        if reserved_user_coupon_id:
            coupon_repo = CouponRepository(self.db)
            success = await coupon_repo.reserve_coupon(reserved_user_coupon_id, order.id)
            if not success:
                # 预留失败，回滚（commit 已在上面，这里抛出异常让上层处理）
                raise ValueError("优惠券预留失败，请重试")

        await self.db.commit()

        # 7. 清空用户购物车
        await self.cart_repo.clear_cart(user_id)

        # expire_time = datetime.now() + timedelta(minutes=30)
        expire_time = datetime.now() + timedelta(minutes=1)
        redis_client = await get_redis()
        await redis_client.zadd(
            "order:pending:timeout",
            {str(order.id): expire_time.timestamp()}
        )

        return order

    async def get_order_detail(self, user_id: int, order_id: int):
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.user_id != user_id:
            raise ValueError("无权访问此订单")
        items = await self.order_repo.get_order_items(order_id)
        return {"order": order, "items": items}

    @observe_order_status_change
    async def update_order_status(self, order_id: int, new_status: str):
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        data =  await self.order_repo.update_status(order, new_status)
        await self.db.commit()
        return data

    async def get_all_orders(self, skip: int = 0, limit: int = 100, status: str = None):
        return await self.order_repo.get_all_orders(skip=skip, limit=limit, status=status)
    
    async def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 20, status: str = None):
        return await self.order_repo.get_user_orders(user_id, skip, limit, status)
    
    async def release_coupon(self, order_id: int):
        """订单超时未支付时，释放预留的优惠券

        由 Redis 订单超时监听器调用
        """
        from app.repository.coupon_repo import CouponRepository
        coupon_repo = CouponRepository(self.db)

        order = await self.order_repo.get_by_id(order_id)
        if not order or not order.coupon_id:
            return  # 没有用优惠券，直接返回

        # 找到该用户对该券的预留记录
        user_coupons = await coupon_repo.get_user_coupons(order.user_id, status="reserved")
        user_coupon = next(
            (uc for uc in user_coupons
            if uc.coupon_id == order.coupon_id and uc.reserved_order_id == order_id),
            None
        )
        if user_coupon:
            await coupon_repo.release_coupon(user_coupon.id)
            await self.db.commit()

    async def cancel_order(self, user_id: int, order_id: int) -> Order:
        """用户取消订单：仅限待支付状态"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.user_id != user_id:
            raise ValueError("无权操作此订单")
        if order.status != OrderStatus.PENDING.value:
            raise ValueError("只有待支付状态的订单可以取消")

        # 1. 回补库存
        await self.order_repo.restore_stock(order_id)

        # 2. 释放优惠券预留
        if order.coupon_id:
            from app.repository.coupon_repo import CouponRepository
            coupon_repo = CouponRepository(self.db)
            user_coupons = await coupon_repo.get_user_coupons(order.user_id, status="reserved")
            user_coupon = next(
                (uc for uc in user_coupons
                 if uc.coupon_id == order.coupon_id and uc.reserved_order_id == order_id),
                None
            )
            if user_coupon:
                await coupon_repo.release_coupon(user_coupon.id)

        # 3. 更新状态
        await self.order_repo.update_status(order, OrderStatus.CANCELLED.value)
        await self.db.commit()
        return await self.order_repo.get_by_id(order_id)

    async def confirm_receipt(self, user_id: int, order_id: int) -> Order:
        """用户确认收货：仅限已发货状态，确认后订单完成"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.user_id != user_id:
            raise ValueError("无权操作此订单")
        if order.status != OrderStatus.SHIPPED.value:
            raise ValueError("只有已发货状态的订单可以确认收货")

        await self.update_order_status(order_id, OrderStatus.COMPLETED.value)
        return await self.order_repo.get_by_id(order_id)
