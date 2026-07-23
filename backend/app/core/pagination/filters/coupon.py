from app.core.pagination.filter import BaseFilter, FilterRange
from app.models.coupon import Coupon
from typing import Optional


class CouponFilter(BaseFilter[Coupon]):
    """Coupon 列表过滤器"""

    # 过滤字段

    # 排序字段（黑名单字段，不参与 to_conditions）
    order_by: Optional[str] = "created_at"
    order_dir: Optional[str] = "desc"

    # 列名映射：filter字段名 → 数据库列名
    column_mapper = {
    }
