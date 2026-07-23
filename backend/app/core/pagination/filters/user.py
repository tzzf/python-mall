from app.core.pagination.filter import BaseFilter, FilterRange
from app.models.user import V1User
from typing import Optional


class V1UserFilter(BaseFilter[V1User]):
    """V1User 列表过滤器"""

    # 过滤字段
    status: Optional[str] = None  # channel_status 的映射
    is_channel: Optional[bool] = None

    # 排序字段（黑名单字段，不参与 to_conditions）
    order_by: Optional[str] = "created_at"
    order_dir: Optional[str] = "desc"

    # 列名映射：filter字段名 → 数据库列名
    column_mapper = {
        "status": "channel_status",
        "is_channel": "is_channel",
    }
