from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CouponBase(BaseModel):
    code: str
    name: str
    discount_type: str  # "fixed" | "percent"
    discount_value: Decimal
    min_order_amount: Decimal = Decimal("0")
    max_discount_amount: Optional[Decimal] = None
    total_count: int
    start_time: datetime
    end_time: datetime


class CouponCreate(CouponBase):
    remain_count: int

    @validator("discount_type")
    def validate_discount_type(cls, v):
        if v not in ("fixed", "percent"):
            raise ValueError("discount_type 必须是 fixed 或 percent")
        return v


class CouponUpdate(BaseModel):
    name: Optional[str] = None
    discount_value: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    total_count: Optional[int] = None
    remain_count: Optional[int] = None
    is_active: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class CouponResponse(CouponBase):
    id: int
    remain_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# === 用户优惠券 ===

class UserCouponResponse(BaseModel):
    id: int
    coupon_id: int
    status: str
    received_at: datetime
    used_at: Optional[datetime] = None
    # 嵌套优惠券信息
    coupon: CouponResponse

    class Config:
        from_attributes = True


class ReceiveCouponRequest(BaseModel):
    coupon_id: int


class UseCouponRequest(BaseModel):
    user_coupon_id: int
    order_id: int


# 响应模型
class CouponInfo(BaseModel):
    """优惠券信息（内部用）"""
    id: int
    code: str
    name: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Decimal
    max_discount_amount: Optional[Decimal] = None
    remain_count: int
    total_count: int
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True


class UserCouponDetail(BaseModel):
    """用户优惠券详情"""
    id: int
    coupon_id: int
    code: str
    name: str
    discount_type: str
    discount_value: Decimal
    status: str
    received_at: datetime

    class Config:
        from_attributes = True


class ReceiveCouponResponse(BaseModel):
    """领取响应"""
    id: int
    coupon_id: int
    code: str
    name: str
    message: str


class DiscountCalculateResponse(BaseModel):
    """折扣计算响应"""
    original_amount: str
    discount_amount: str
    final_amount: str
    coupon_code: str


class UseCouponResponse(BaseModel):
    """使用优惠券响应"""
    message: str
    order_id: int


class UpdateCouponResponse(BaseModel):
    """更新优惠券响应"""
    id: int
    code: str
    name: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Decimal
    max_discount_amount: Optional[Decimal] = None
    total_count: int
    remain_count: int
    is_active: bool
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True
