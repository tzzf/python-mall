from dataclasses import dataclass
from typing import Generic, TypeVar, List

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    """分页返回结构，所有分页接口统一使用此容器"""

    items: List[T]
    total: int
    page: int
    page_size: int
    has_next_page: bool

    @classmethod
    def build(
        cls,
        items: List[T],
        total: int,
        skip: int = 0,
        limit: int = 20,
    ) -> "PaginatedResult[T]":
        page = skip // limit + 1 if limit > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            has_next_page=skip + limit < total,
        )
