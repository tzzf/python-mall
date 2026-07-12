from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.repository.order_repo import OrderRepository
from app.repository.product_repo import ProductRepository
from app.repository.coupon_repo import CouponRepository
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.core.redis import get_redis
import logging


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


def create_scheduler():
    scheduler = AsyncIOScheduler()

    # 每 1 分钟检查一次超时订单
    scheduler.add_job(
        check_expired_orders,
        trigger=IntervalTrigger(minutes=1),
        id="check_expired_orders",
        replace_existing=True,
    )

    # 每 5 分钟检查一次超时库存锁
    scheduler.add_job(
        check_expired_locks,
        trigger=IntervalTrigger(minutes=5),
        id="check_expired_locks",
        replace_existing=True,
    )

    return scheduler

async def check_expired_orders():
    """
    从 Redis Sorted Set 获取超时的 pending 订单，批量处理
    """
    redis_client = await get_redis()
    try:
        now = datetime.now().timestamp()
        logger.debug(f"[check_expired_orders] 开始执行, now={now}")
        
        # 取出所有已超时的订单 ID（分数 < 当前时间戳）
        expired_order_ids = await redis_client.zrangebyscore(
            "order:pending:timeout",
            "-inf",
            now,
            withscores=False
        )
        logger.info(f"[check_expired_orders] Redis 查询到 {len(expired_order_ids)} 个超时订单")
        
        if not expired_order_ids:
            logger.info("[check_expired_orders] 没有超时订单，直接返回")
            return
        
        # 从 Redis 删除（原子操作）
        logger.debug(f"[check_expired_orders] 从 Redis 删除: {expired_order_ids}")
        await redis_client.zrem("order:pending:timeout", *expired_order_ids)
        
        # 批量查 DB，更新状态 + 还原库存
        async with AsyncSessionLocal() as db:
            order_repo = OrderRepository(db)
            product_repo = ProductRepository(db)
            coupon_repo = CouponRepository(db)
            
            for order_id_bytes in expired_order_ids:
                order_id = int(order_id_bytes)
                logger.debug(f"[check_expired_orders] 处理订单 {order_id}")
                
                try:
                    # 更新状态
                    order = await order_repo.get_by_id(order_id)
                    if not order:
                        raise ValueError("订单不存在")
                    if order.status != "pending":
                        raise ValueError("订单状态不正确")
                    
                    # 还原库存
                    order_items = await order_repo.get_order_items(order_id)
                    for item in order_items:
                        await product_repo.increase_stock(item.product_id, item.quantity)
                    
                    if order.coupon_id:
                        user_coupons = await coupon_repo.get_user_coupons(
                            order.user_id, status="reserved"
                        )
                        user_coupon = next(
                            (uc for uc in user_coupons
                            if uc.coupon_id == order.coupon_id
                            and uc.reserved_order_id == order_id),
                            None
                        )
                        if user_coupon:
                            await coupon_repo.release_coupon(user_coupon.id)

                    await order_repo.update_status(order, "cancelled")


                    logger.info(f"[check_expired_orders] 订单 {order_id} 已取消")
                except Exception as e:
                    logger.error(f"[check_expired_orders] 处理订单 {order_id} 失败: {e}", exc_info=True)
                    raise  # 让 APScheduler 知道任务失败了
            
            await db.commit()

        logger.info(f"[check_expired_orders] 全部完成，共取消 {len(expired_order_ids)} 个订单")
        
        print(f"[scheduler] 取消了 {len(expired_order_ids)} 个超时订单")
        
    finally:
        await redis_client.close()


async def check_expired_locks():
    """
    检查超时的库存锁，释放锁定
    （如果库存锁有独立表的话，目前简化处理，库存锁在订单取消时一起释放）
    """
    # 当前设计：库存锁在订单取消时一起还原（见上面 check_expired_orders）
    # 如果以后有独立的库存锁表，在这里处理
    pass
