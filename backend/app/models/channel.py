from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime
from decimal import Decimal


class ChannelInviteCode(Base):
    """渠道商邀请码表"""
    __tablename__ = "channel_invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False, unique=True)  # 一个渠道商一个邀请码
    invite_code = Column(String(20), unique=True, index=True, nullable=False)
    is_custom = Column(Integer, default=0)  # 0=系统生成 1=自定义
    created_at = Column(DateTime, default=datetime.utcnow)


class ChannelApplication(Base):
    """渠道商申请表"""
    __tablename__ = "channel_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False, unique=True)  # 一个用户只能申请一次
    status = Column(String(20), default="pending", index=True)  # pending/approved/rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    reject_reason = Column(String(255), nullable=True)


class ChannelBank(Base):
    """渠道商银行卡表"""
    __tablename__ = "channel_banks"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False, unique=True)
    bank_name = Column(String(50), nullable=False)  # 银行名称
    bank_account = Column(String(50), nullable=False)  # 银行卡号
    account_holder = Column(String(50), nullable=False)  # 开户人姓名
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChannelCommission(Base):
    """渠道商佣金明细表"""
    __tablename__ = "channel_commissions"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 1=L1 2=L2
    amount = Column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    balance = Column(Numeric(10, 2), nullable=False, default=Decimal("0"))  # 可用余额 = amount - 已提现
    status = Column(String(20), default="frozen", index=True)  # frozen/available/withdrawn
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # 幂等性：同一订单同一渠道商同一层级只能有一条记录
        UniqueConstraint("order_id", "channel_id", "level", name="uq_order_channel_level"),
        Index("ix_channel_commissions_order_channel", "order_id", "channel_id"),
    )


class ChannelWithdrawal(Base):
    """渠道商提现记录表"""
    __tablename__ = "channel_withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("v1_users.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", index=True)  # pending/approved/rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    reject_reason = Column(String(255), nullable=True)


class ChannelSetting(Base):
    """渠道商佣金比例配置表"""
    __tablename__ = "channel_settings"

    id = Column(Integer, primary_key=True, index=True)
    l1_rate = Column(Numeric(5, 4), nullable=False, default=Decimal("0.1000"))  # L1佣金比例，如 0.1000 = 10%
    l2_rate = Column(Numeric(5, 4), nullable=False, default=Decimal("0.0500"))  # L2佣金比例，如 0.0500 = 5%
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderChannel(Base):
    """订单渠道关系表（支付成功时写入）"""
    __tablename__ = "order_channels"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)  # 一笔订单只能有一条渠道记录
    l1_channel_id = Column(Integer, ForeignKey("v1_users.id"), nullable=True)  # L1渠道商
    l2_channel_id = Column(Integer, ForeignKey("v1_users.id"), nullable=True)  # L2渠道商
    actual_amount = Column(Numeric(10, 2), nullable=False)  # 实际成交价（下单时快照）
    created_at = Column(DateTime, default=datetime.utcnow)
