from app.core.pagination.filter import BaseFilter
from app.models.channel import ChannelApplication, ChannelWithdrawal
from app.models.user import V1User
from typing import Optional


class ChannelApplicationFilter(BaseFilter[ChannelApplication]):
    """渠道商申请分页过滤器"""

    status: Optional[str] = None
    order_by: Optional[str] = "created_at"
    order_dir: Optional[str] = "desc"

    def get_joins(self, model_class: type[ChannelApplication]) -> list:
        return [(V1User, ChannelApplication.user_id == V1User.id)]

    def get_join_columns(self, model_class: type[ChannelApplication]) -> list:
        return [V1User.username]


class ChannelWithdrawalFilter(BaseFilter[ChannelWithdrawal]):
    """渠道商提现分页过滤器"""

    status: Optional[str] = None
    order_by: Optional[str] = "created_at"
    order_dir: Optional[str] = "desc"

    def get_joins(self, model_class: type[ChannelWithdrawal]) -> list:
        return [(V1User, ChannelWithdrawal.channel_id == V1User.id)]

    def get_join_columns(self, model_class: type[ChannelWithdrawal]) -> list:
        return [V1User.username]
