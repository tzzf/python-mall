from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime


class V1User(Base):
    __tablename__ = "v1_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 渠道商相关
    is_channel = Column(Boolean, default=False, index=True)  # 是否是渠道商
    channel_status = Column(String(20), default="pending", index=True)  # pending/approved/rejected
    referrer_id = Column(Integer, ForeignKey("v1_users.id"), nullable=True)  # 上级用户ID

    # 关系
    referrer = relationship("V1User", remote_side=[id], backref="referrals")


# 管理员用户表（admin 管理端）
class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
