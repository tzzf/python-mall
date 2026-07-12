from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from app.schemas.coupon import CouponResponse


class OrderStatus(str, Enum):
    PENDING = "pending"           # 待支付
    PAID = "paid"                 # 已支付
    SHIPPED = "shipped"           # 已发货
    DELIVERED = "delivered"       # 已收货/已完成
    CANCELLED = "cancelled"       # 已取消
    REFUNDING = "refunding"       # 退款中
    REFUNDED = "refunded"         # 已退款


# === 请求 ===

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    address: str
    items: List[OrderItemCreate]  # 购物车直接结算，或立刻购买
    coupon_code: Optional[str] = None  # 用户传入的优惠券码


# === 响应 ===

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: Decimal
    quantity: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatus
    address: str
    items: List[OrderItemResponse]
    created_at: datetime
    coupon_id: int | None
    coupon_discount: Decimal
    coupon: Optional[CouponResponse] = None

    class Config:
        from_attributes = True


# === 状态更新 ===

class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderCancelResponse(BaseModel):
    id: int
    status: OrderStatus
    message: str


class OrderConfirmReceiptResponse(BaseModel):
    id: int
    status: OrderStatus
    message: str


class PaginatedOrdersResponse(BaseModel):
    data: List[OrderResponse]
    total: int
    skip: int
    limit: int
