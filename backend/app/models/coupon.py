from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    discount_type = Column(String(20), nullable=False)  # "fixed" | "percent"
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    min_order_amount = Column(DECIMAL(10, 2), default=0)
    max_discount_amount = Column(DECIMAL(10, 2), nullable=True)
    total_count = Column(Integer, nullable=False)
    remain_count = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserCoupon(Base):
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    status = Column(String(20), default="unused")  # "unused" | "used" | "expired" ｜ "reserved" 
    received_at = Column(DateTime, server_default=func.now())
    used_at = Column(DateTime, nullable=True)
    reserved_order_id = Column(Integer, nullable=True)  # 预留给哪个订单

    # 关联
    user = relationship("V1User", backref="user_coupons")
    coupon = relationship("Coupon", backref="user_coupons")
