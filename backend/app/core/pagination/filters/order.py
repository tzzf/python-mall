from app.core.pagination.filter import BaseFilter, FilterRange
from app.models.order import Order
from typing import TypeVar
from typing import Optional
from sqlalchemy.orm import selectinload

M = TypeVar("M")


class OrderFilter(BaseFilter[Order]):
    """Order 列表过滤器"""

    # 过滤字段
    status: Optional[str] = None
    user_id: Optional[int] = None

    # 排序字段（黑名单字段，不参与 to_conditions）
    order_by: Optional[str] = "id"
    order_dir: Optional[str] = "desc"

    # 列名映射：filter字段名 → 数据库列名
    column_mapper = {
        "status": "status",
        "user_id": "user_id"
    }

    def get_options(self, model_class: type[M]) -> list:
        return [
            selectinload(model_class.items),
            selectinload(model_class.coupon),
        ]
