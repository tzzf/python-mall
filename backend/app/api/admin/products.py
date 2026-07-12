from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.service.product_service import ProductService, CategoryService
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    PaginatedSpuResponse,
)
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["管理端-商品"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


# === Category ===

@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_category_service(db)
    return await svc.create_category(category_in)


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_category_service(db)
    return await svc.list_categories()


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_category_service(db)
    try:
        return await svc.update_category(category_id, category_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_category_service(db)
    try:
        await svc.delete_category(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# === Product ===

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_product_service(db)
    return await svc.create_product(product_in)


@router.get("/", response_model=PaginatedSpuResponse)
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_product_service(db)
    return await svc.list_products(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_product_service(db)
    product = await svc.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_product_service(db)
    try:
        return await svc.update_product(product_id, product_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    svc = get_product_service(db)
    try:
        await svc.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
