from pydantic import BaseModel
from typing import Any, Generic, TypeVar, Optional, ClassVar
from sqlalchemy.sql import ColumnElement
from sqlalchemy import and_


M = TypeVar("M")  # SQLAlchemy 模型类型


class FilterRange(BaseModel, Generic[M]):
    """范围查询值对象，生成 column >= start AND column <= end"""

    start: Optional[Any] = None
    end: Optional[Any] = None

    def to_sql(self, column) -> ColumnElement:
        conditions = []
        if self.start is not None:
            conditions.append(column >= self.start)
        if self.end is not None:
            conditions.append(column <= self.end)
        if conditions:
            return and_(*conditions)
        return None


class FilterBetween(BaseModel, Generic[M]):
    """区间查询值对象，生成 column > start AND column < end"""

    start: Optional[Any] = None
    end: Optional[Any] = None

    def to_sql(self, column) -> ColumnElement:
        conditions = []
        if self.start is not None:
            conditions.append(column > self.start)
        if self.end is not None:
            conditions.append(column < self.end)
        if conditions:
            return and_(*conditions)
        return None


# 不参与 to_conditions 的特殊字段（排序、分页等）
EXCLUDE_FIELDS = {"order_by", "order_dir"}


class BaseFilter(BaseModel, Generic[M]):
    """
    分页过滤器基类。

    子类通过以下方式使用：
    1. 定义 filter 字段 + column_mapper 映射
    2. 可选 override custom_conditions() 添加复杂查询

    Example:
        class V1UserFilter(BaseFilter[V1User]):
            status: Optional[str] = None
            level: Optional[FilterRange[int]] = None
            order_by: Optional[str] = "created_at"
            order_dir: Optional[str] = "desc"

            column_mapper = {
                "status": "channel_status",
                "level": "level",
            }

            def custom_conditions(self) -> list[ColumnElement]:
                return []
    """

    # 列名映射：filter 字段名 → 数据库列名
    column_mapper: ClassVar[dict[str, str]] = {}

    def to_conditions(self, model_class: type[M]) -> dict[str, list[ColumnElement]]:
        """
        将 filter 字段转换为按列名分组的 SQLAlchemy 条件列表。

        返回格式:
            {
                "column_name": [condition1, condition2, ...],
                ...
            }
        """
        conditions_by_column: dict[str, list[ColumnElement]] = {}
        data = self.model_dump(exclude_none=False)

        for field_name, value in data.items():
            if field_name in EXCLUDE_FIELDS:
                continue
            if value is None:
                continue

            # 获取实际列名
            column_name = self.column_mapper.get(field_name, field_name)
            column = getattr(model_class, column_name, None)
            if column is None:
                continue

            # 根据值类型生成 SQL 条件
            sql_cond = self._value_to_sql(column, value)
            if sql_cond is not None:
                if column_name not in conditions_by_column:
                    conditions_by_column[column_name] = []
                conditions_by_column[column_name].append(sql_cond)

        return conditions_by_column

    def _value_to_sql(self, column, value: Any) -> Optional[ColumnElement]:
        """根据值的类型分发到不同的 SQL 生成器"""
        # FilterRange / FilterBetween 自己知道怎么转 SQL
        if isinstance(value, (FilterRange, FilterBetween)):
            return value.to_sql(column)
        # 普通值：等值查询
        return column == value

    def custom_conditions(self, model_class: type[M]) -> list[ColumnElement]:
        """
        扩展钩子：子类可 override 此方法返回复杂查询条件。
        默认返回空列表。
        """
        return []

    def get_options(self, model_class: type[M]) -> list[Any]:
        """扩展钩子：子类可 override 此方法返回要 eager load 的关系选项"""
        return []

    def get_order_by(self) -> tuple[Optional[str], Optional[str]]:
        """返回 (order_by 列名, order_dir)"""
        return self.order_by, self.order_dir

    def get_joins(self, model_class: type[M]) -> list[tuple[type, Any]]:
        """
        子类可 override，返回要 JOIN 的 [(目标模型, ON条件), ...]。
        默认为空列表（无 JOIN）。
        """
        return []

    def get_join_columns(self, model_class: type[M]) -> list[Any]:
        """
        子类可 override，返回 JOIN 后额外要 SELECT 的列（如 username）。
        这些列的值会随 items 一起返回，供调用方构造响应。
        """
        return []
