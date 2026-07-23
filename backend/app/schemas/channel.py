from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal


def beijing_time(v: datetime) -> str:
    if v is None:
        return None
    beijing_tz = timezone(timedelta(hours=8))
    bt = v.replace(tzinfo=timezone.utc).astimezone(beijing_tz)
    return bt.isoformat()


# ============ 邀请码 ============

class InviteCodeResponse(BaseModel):
    invite_code: str
    is_custom: bool

    class Config:
        from_attributes = True


# ============ 渠道商申请 ============

class ChannelApplyResponse(BaseModel):
    status: str
    message: str

    class Config:
        from_attributes = True


# ============ 银行卡 ============

class ChannelBankCreate(BaseModel):
    bank_name: str
    bank_account: str
    account_holder: str


class ChannelBankResponse(BaseModel):
    id: int
    channel_id: int
    bank_name: str
    bank_account: str
    account_holder: str
    created_at: datetime

    @field_serializer("created_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


# ============ 佣金明细 ============

class ChannelCommissionResponse(BaseModel):
    id: int
    order_id: int
    level: int  # 1=L1 2=L2
    amount: Decimal
    balance: Decimal
    status: str  # frozen/available/withdrawn
    created_at: datetime

    @field_serializer("created_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


class ChannelCommissionSummary(BaseModel):
    """渠道商佣金汇总"""
    total_frozen: Decimal = Decimal("0")
    total_available: Decimal = Decimal("0")
    total_withdrawn: Decimal = Decimal("0")


# ============ 提现 ============

class WithdrawalRequest(BaseModel):
    amount: Decimal


class WithdrawalResponse(BaseModel):
    id: int
    channel_id: int
    amount: Decimal
    status: str
    created_at: datetime

    @field_serializer("created_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


# ============ 渠道商资料（前台） ============

class ChannelProfileResponse(BaseModel):
    """渠道商个人信息（前台用）"""
    id: int
    username: str
    is_channel: bool
    channel_status: str
    referrer_id: Optional[int] = None
    bank: Optional[ChannelBankResponse] = None
    commission_summary: ChannelCommissionSummary

    class Config:
        from_attributes = True


# ============ 我的下级 ============

class ReferralUserInfo(BaseModel):
    """下级用户信息"""
    id: int
    username: str
    created_at: datetime

    @field_serializer("created_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


class MyReferralsResponse(BaseModel):
    """我的下级列表"""
    l1_referrals: list[ReferralUserInfo] = []  # 直接下级
    l2_referrals: list[ReferralUserInfo] = []  # 二级下级（下级的下级）


# ============ 管理员用 Schema ============

class ChannelApplicationItem(BaseModel):
    """渠道商申请记录（管理员查看）"""
    id: int
    user_id: int
    username: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reject_reason: Optional[str] = None

    @field_serializer("created_at", "reviewed_at")
    def convert_to_beijing(self, v: Optional[datetime]) -> Optional[str]:
        return beijing_time(v)

    class Config:
        from_attributes = True


class ChannelApplicationReviewRequest(BaseModel):
    """审核申请"""
    action: str  # approved / rejected
    reject_reason: Optional[str] = None


class ChannelListItem(BaseModel):
    """渠道商列表项（管理员查看）"""
    id: int # 用户id
    username: str
    is_channel: bool
    channel_status: str
    referrer_id: Optional[int] = None
    created_at: datetime

    @field_serializer("created_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


class ChannelSettingUpdate(BaseModel):
    """更新佣金比例配置"""
    l1_rate: Decimal
    l2_rate: Decimal


class ChannelSettingResponse(BaseModel):
    l1_rate: Decimal
    l2_rate: Decimal
    updated_at: datetime

    @field_serializer("updated_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


class WithdrawalReviewRequest(BaseModel):
    """提现审核"""
    action: str  # approved / rejected
    reject_reason: Optional[str] = None


class WithdrawalListItem(BaseModel):
    """提现记录列表项"""
    id: int
    channel_id: int
    username: str
    amount: Decimal
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reject_reason: Optional[str] = None

    @field_serializer("created_at", "reviewed_at")
    def convert_to_beijing(self, v: Optional[datetime]) -> Optional[str]:
        return beijing_time(v)

    class Config:
        from_attributes = True


class ChannelOrderDetail(BaseModel):
    """渠道商订单明细"""
    order_id: int
    actual_amount: Decimal
    l1_amount: Optional[Decimal] = None
    l2_amount: Optional[Decimal] = None
    order_created_at: datetime

    @field_serializer("order_created_at")
    def convert_to_beijing(self, v: datetime) -> str:
        return beijing_time(v)

    class Config:
        from_attributes = True


# ============ 分页响应 ============

class PaginatedResponse(BaseModel):
    """通用分页响应"""
    data: list
    total: int
    skip: Optional[int] = None
    page: Optional[int] = None
    limit: int
