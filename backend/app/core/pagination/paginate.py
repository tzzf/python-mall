from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import TypeVar
from app.core.pagination.result import PaginatedResult
from app.core.pagination.filter import BaseFilter

M = TypeVar("M")


async def paginate(
    db: AsyncSession,
    model_class: type[M],
    filters: BaseFilter[M],
    skip: int = 0,
    limit: int = 20,
) -> PaginatedResult[M]:
    """
    通用分页函数。

    使用方式：
        filters = V1UserFilter(status="approved", level=FilterRange(start=3))
        result = await paginate(self.db, V1User, filters, skip=0, limit=20)

    - filter 条件通过 filters.to_conditions() + filters.custom_conditions() 生成
    - count query 和 data query 分离：count 只查目标表主键数量，不带 JOIN/ORDER BY/options
    - 排序字段从 filters.order_by / filters.order_dir 读取
    - 支持 override filters.get_options() 添加 selectinload 等急加载
    - 支持 override filters.get_joins() + filters.get_join_columns() 做 JOIN 查额外列
    """
    # 1. 收集所有 where 条件（count 和 data 共享同一套条件）
    conditions_by_column = filters.to_conditions(model_class)
    custom_conditions = filters.custom_conditions(model_class)

    all_conditions: list = []
    for column_conditions in conditions_by_column.values():
        all_conditions.extend(column_conditions)
    all_conditions.extend(custom_conditions)

    # 读取 JOIN 配置
    join_specs: list = filters.get_joins(model_class)
    extra_columns: list = filters.get_join_columns(model_class)
    has_join = bool(join_specs)

    # 2. Count 查询
    count_col = getattr(model_class, "id", None)
    if count_col is None:
        count_col = model_class.__table__.primary_key.columns.values()[0]
    count_query = select(func.count(count_col))
    for target_model, on_condition in join_specs:
        count_query = count_query.join(target_model, on_condition)
    if all_conditions:
        count_query = count_query.where(and_(*all_conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # 3. 主查询
    if has_join or extra_columns:
        # JOIN 模式：SELECT 主模型 + 额外列
        query = select(model_class, *extra_columns)
        for target_model, on_condition in join_specs:
            query = query.join(target_model, on_condition)
    else:
        # 普通模式
        opts = filters.get_options(model_class)
        if opts:
            query = select(model_class).options(*opts)
        else:
            query = select(model_class)

    order_by_col = filters.order_by or "created_at"
    order_dir = filters.order_dir or "desc"
    sort_column = getattr(model_class, order_by_col, None)
    if sort_column is not None:
        query = query.order_by(
            sort_column.desc() if order_dir == "desc" else sort_column.asc()
        )
    else:
        query = query.order_by(model_class.created_at.desc())

    if all_conditions:
        query = query.where(and_(*all_conditions))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)

    if has_join or extra_columns:
        rows = result.all()
        return PaginatedResult.build(rows, total, skip, limit)
    else:
        items = list(result.scalars().all())
        return PaginatedResult.build(items, total, skip, limit)
