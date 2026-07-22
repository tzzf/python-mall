from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# === Category ===

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

    @validator("parent_id", pre=True, always=True)
    def convert_zero_to_none(cls, v):
        if v == 0 or v == "" or v is None:
            return None
        return v

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int]

    class Config:
        from_attributes = True



# === Product ===

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int = 0
    is_active: bool = True
    category_id: Optional[int] = None
    image: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    image: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedSpuResponse(BaseModel):
    data: List[ProductResponse]
    total: int
    skip: int
    limit: int
