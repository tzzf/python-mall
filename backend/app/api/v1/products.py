from app.schemas.channel import PaginatedResponse
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.product_service import ProductService, CategoryService
from app.schemas.product import ProductResponse, CategoryResponse, PaginatedSpuResponse
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["用户端-商品"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@router.get("/")
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    svc: ProductService = Depends(get_product_service),
):
    result = await svc.list_products(skip, limit, category_id)
    data = [
        ProductResponse.model_validate(c, from_attributes=True)
        for c in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, skip=skip, page=result.page, limit=result.page_size)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    svc: ProductService = Depends(get_product_service),
):
    return await svc.get_product(product_id)


@router.get("/categories/")
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    svc: CategoryService = Depends(get_category_service),
):
    result = await svc.list_categories(skip, limit)
    data = [
        CategoryResponse.model_validate(c, from_attributes=True)
        for c in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, skip=skip, page=result.page, limit=result.page_size)
