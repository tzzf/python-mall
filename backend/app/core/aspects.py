"""
AOP 切面：监听订单状态变更，触发佣金计算

pending → paid     : 冻结佣金（写入 OrderChannel + 创建佣金冻结记录）
paid → completed   : 解冻佣金（frozen → available）
"""
from functools import wraps
from decimal import Decimal


def observe_order_status_change(func):
    """
    装饰器：监听订单状态变更，触发佣金相关逻辑

    适用于 OrderService 的 update_status 相关方法。
    会在状态变更为 paid 时调用 on_order_paid，
    变更为 completed 时调用 on_order_completed。
    """
    @wraps(func)
    async def wrapper(self, order_id: int, new_status: str, *args, **kwargs):
        # 先执行原逻辑（更新状态）
        result = await func(self, order_id, new_status, *args, **kwargs)

        # 状态变更后，触发佣金计算
        from app.service.channel_service import CommissionService
        from app.core.database import get_db

        # 获取订单的实际成交价（total_amount - coupon_discount）
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return result

        actual_amount = order.total_amount  # 已是折后价

        async for db in get_db():
            commission_svc = CommissionService(db)
            if new_status == "paid":
                await commission_svc.on_order_paid(order_id, Decimal(str(actual_amount)))
            elif new_status == "completed":
                await commission_svc.on_order_completed(order_id)
            break

        return result

    return wrapper
