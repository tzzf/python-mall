from app.core.pagination.filter import BaseFilter, FilterRange
from app.models.product import Category
from typing import Optional


class CategoryFilter(BaseFilter[Category]):
    """Category 列表过滤器"""

    # 排序字段（黑名单字段，不参与 to_conditions）
    order_by: Optional[str] = "id"
    order_dir: Optional[str] = "desc"

    # 列名映射：filter字段名 → 数据库列名
    column_mapper = {
    }
