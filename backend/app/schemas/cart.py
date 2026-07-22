from pydantic import BaseModel
from typing import List, Optional

class CartItemAdd(BaseModel):
    """添加商品到购物车"""
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    """修改购物车商品数量"""
    quantity: int


class CartItemResponse(BaseModel):
    """购物车商品项"""
    product_id: int
    quantity: int
    product_name: Optional[str] = None
    price: Optional[str] = None
    image: Optional[str] = None


class CartResponse(BaseModel):
    """购物车"""
    user_id: int
    items: List[CartItemResponse]
    total_count: int
