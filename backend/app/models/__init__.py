from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import V1User, AdminUser
from app.models.channel import (
    ChannelInviteCode,
    ChannelApplication,
    ChannelBank,
    ChannelCommission,
    ChannelWithdrawal,
    ChannelSetting,
    OrderChannel,
)
