from sqlalchemy import Column, Integer, String, DECIMAL, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime
from decimal import Decimal

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")  # pending/paid/shipped/delivered/cancelled/refunded
    address = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=True)
    coupon_discount = Column(DECIMAL(10, 2), default=Decimal("0"))

    items = relationship("OrderItem", back_populates="order")
    coupon = relationship("Coupon", backref="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
