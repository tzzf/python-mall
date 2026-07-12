from app.repository.order_repo import OrderRepository
from app.service.order_service import OrderService
import random
import string

class PayService:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    def _generate_pay_url(self, order_id: int) -> str:
        """模拟生成支付链接"""
        fake_order_no = "".join(random.choices(string.ascii_uppercase + string.digits, k=32))
        return f"https://pay.example.com/qr?order={fake_order_no}"

    async def create_pay(self, user_id: int, order_id: int) -> dict:
        """
        1. 验证订单存在且属于当前用户
        2. 验证订单状态是 pending
        3. 生成模拟支付链接
        """
        # 获取订单详情
        result = await self.order_service.get_order_detail(user_id, order_id)
        order = result["order"]

        # 状态校验：只有 pending 可以支付
        if order.status != "pending":
            raise ValueError(f"订单状态不是待支付，当前状态: {order.status}")

        # 生成模拟支付链接
        pay_url = self._generate_pay_url(order_id)

        return {
            "order_id": order_id,
            "pay_url": pay_url,
            "qr_code": f"order-{order_id}-pay",
            "amount": str(order.total_amount),
        }

    async def pay_callback(self, user_id: int, order_id: int, pay_status: str, transaction_id: str = None) -> dict:
        """
        支付回调
        1. 验证订单存在且属于当前用户
        2. 验证订单状态是 pending（未超时）
        3. 更新订单状态
        """
        result = await self.order_service.get_order_detail(user_id, order_id)
        order = result["order"]

        if order.status != "pending":
            raise ValueError(f"订单状态不是待支付，无法回调。当前状态: {order.status}")

        if pay_status == "success":
            # 更新为已支付
            await self.order_service.update_order_status(order_id, "paid")

            # 核销预留的优惠券
            from app.repository.coupon_repo import CouponRepository
            from app.service.coupon_service import CouponService
            # 获取该订单关联的优惠券信息
            if order.coupon_id:
                from app.core.database import get_db
                async for db in get_db():
                    coupon_repo = CouponRepository(db)
                    # 找到该用户该券的预留记录
                    user_coupons = await coupon_repo.get_user_coupons(user_id, status="reserved")
                    user_coupon = next(
                        (uc for uc in user_coupons
                        if uc.coupon_id == order.coupon_id and uc.reserved_order_id == order_id),
                        None
                    )
                    if user_coupon:
                        coupon_svc = CouponService(db, coupon_repo)
                        await coupon_svc.use_coupon(user_coupon.id, order_id)
                    break

            return {
                "code": 200,
                "message": "支付成功",
                "transaction_id": transaction_id,
            }
        else:
            return {
                "code": 400,
                "message": "支付失败",
                "transaction_id": transaction_id,
            }
