from app.core.pagination.filter import BaseFilter, FilterRange
from typing import Optional, TypeVar
from app.models.channel import OrderChannel

M = TypeVar("M")

class OrderChannelFilter(BaseFilter[OrderChannel]):
    """OrderChannel 列表过滤器"""

    channel_id: Optional[int] = None  # 普通 int 值，不走 _value_to_sql 的特殊逻辑
    
    # 排序字段（黑名单字段，不参与 to_conditions）
    order_by: Optional[str] = "id"
    order_dir: Optional[str] = "desc"

    # 列名映射：filter字段名 → 数据库列名
    column_mapper = {
    }

    def custom_conditions(self, model_class: type[M]) -> list:
        from sqlalchemy import or_
        conditions = []
        if self.channel_id is not None:
            conditions.append(or_(
                OrderChannel.l1_channel_id == self.channel_id,
                OrderChannel.l2_channel_id == self.channel_id,
            ))
        return conditions
