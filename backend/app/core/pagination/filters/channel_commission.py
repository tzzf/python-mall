from app.core.pagination.filter import BaseFilter, FilterRange
from typing import Optional
from app.models.channel import ChannelCommission


class ChannelCommissionFilter(BaseFilter[ChannelCommission]):
    """ChannelCommission 列表过滤器"""

    # 过滤字段
    status: Optional[str] = None
    channel_id: Optional[int] = None
    
    # 排序字段（黑名单字段，不参与 to_conditions）
    order_by: Optional[str] = "id"
    order_dir: Optional[str] = "desc"

    # 列名映射：filter字段名 → 数据库列名
    column_mapper = {
        "channel_id": "channel_id",
        "status": "status"
    }
