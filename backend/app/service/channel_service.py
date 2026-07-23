from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repository.channel_repo import ChannelRepository
from app.repository.user_repo import V1UserRepository
from app.models.channel import (
    ChannelInviteCode,
    ChannelApplication,
    ChannelBank,
    ChannelCommission,
    ChannelWithdrawal,
    ChannelSetting,
    OrderChannel,
)
from app.models.order import Order
from app.schemas.channel import (
    ChannelBankCreate,
    ChannelCommissionSummary,
    WithdrawalRequest,
)
from app.core.exceptions import BizException
from datetime import datetime
from decimal import Decimal
import random
import string


def generate_invite_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


class ChannelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ChannelRepository(db)
        self.user_repo = V1UserRepository(db)

    # ============ 邀请码 ============

    async def get_my_invite_code(self, user_id: int) -> ChannelInviteCode:
        code = await self.repo.get_invite_code_by_channel_id(user_id)
        if not code:
            raise BizException("您还不是渠道商")
        return code

    async def set_custom_invite_code(self, user_id: int, code: str) -> ChannelInviteCode:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_channel or user.channel_status != "approved":
            raise BizException("您还不是有效的渠道商")

        if len(code) < 4 or len(code) > 20:
            raise BizException("邀请码长度需在4-20位之间")
        if not code.isalnum():
            raise BizException("邀请码只能包含字母和数字")

        # 查邀请码是否已被占用
        if await self.repo.is_invite_code_used_by_others(code, user_id):
            raise BizException("该邀请码已被使用")

        existing = await self.repo.get_invite_code_by_channel_id(user_id)
        if existing:
            existing.invite_code = code.upper()
            existing.is_custom = 1
            return await self.repo.update_invite_code(existing)
        else:
            new_code = ChannelInviteCode(
                channel_id=user_id,
                invite_code=code.upper(),
                is_custom=1,
            )
            return await self.repo.create_invite_code(new_code)

    # ============ 申请成为渠道商 ============

    async def apply_to_be_channel(self, user_id: int) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise BizException("用户不存在")
        if user.is_channel and user.channel_status == "approved":
            raise BizException("您已经是渠道商")
        if user.is_channel and user.channel_status == "pending":
            raise BizException("您的申请正在审核中")

        existing_app = await self.repo.get_application_by_user_id(user_id)
        if existing_app and existing_app.status == "pending":
            raise BizException("您已提交过申请，请等待审核")

        if existing_app and user.channel_status == "rejected":
            app = ChannelApplication(user_id=user_id, status="pending")
            await self.repo.update_application(app)
            return  {"status": "pending", "message": "申请已重新提交，请等待管理员审核"}

        # 创建申请记录
        app = ChannelApplication(user_id=user_id, status="pending")
        await self.repo.create_application(app)
        return {"status": "pending", "message": "申请已提交，请等待管理员审核"}

    # ============ 银行卡 ============

    async def get_my_bank(self, user_id: int) -> ChannelBank | None:
        return await self.repo.get_bank_by_channel_id(user_id)

    async def save_my_bank(self, user_id: int, bank_in: ChannelBankCreate) -> ChannelBank:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_channel or user.channel_status != "approved":
            raise BizException("您还不是渠道商，无法绑定银行卡")

        bank = ChannelBank(
            channel_id=user_id,
            bank_name=bank_in.bank_name,
            bank_account=bank_in.bank_account,
            account_holder=bank_in.account_holder,
        )
        return await self.repo.upsert_bank(bank)

    # ============ 佣金 ============

    async def get_my_commissions(
        self, user_id: int, status: str | None = None, skip: int = 0, limit: int = 50
    ):
        return await self.repo.get_commissions_by_channel(user_id, status, skip, limit)

    async def get_my_commission_summary(self, user_id: int) -> ChannelCommissionSummary:
        summary = await self.repo.get_commission_summary(user_id)
        return ChannelCommissionSummary(
            total_frozen=summary.get("frozen", Decimal("0")),
            total_available=summary.get("available", Decimal("0")),
            total_withdrawn=summary.get("withdrawn", Decimal("0")),
        )

    # ============ 提现 ============

    async def apply_withdrawal(self, user_id: int, amount: Decimal) -> ChannelWithdrawal:
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_channel or user.channel_status != "approved":
            raise BizException("您还不是渠道商")

        if amount <= 0:
            raise BizException("提现金额必须大于0")

        # 检查可提现余额
        summary = await self.repo.get_commission_summary(user_id)
        available = summary.get("available", Decimal("0"))
        if amount > available:
            raise BizException(f"可提现余额不足，当前可提现 {available}")

        # 检查是否有待处理的提现申请
        # 简化处理：允许同时有多个申请，管理员自行判断

        withdrawal = ChannelWithdrawal(
            channel_id=user_id,
            amount=amount,
            status="pending",
        )
        return await self.repo.create_withdrawal(withdrawal)

    # ============ 我的下级 ============

    async def get_my_referrals(self, user_id: int) -> dict:
        l1 = await self.repo.get_l1_referrals(user_id)
        l2 = await self.repo.get_l2_referrals(user_id)
        return {
            "l1_referrals": l1,
            "l2_referrals": l2,
        }

    # ============ 渠道商资料（前台汇总） ============

    async def get_my_profile(self, user_id: int) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise BizException("用户不存在")

        bank = await self.repo.get_bank_by_channel_id(user_id)
        summary = await self.repo.get_commission_summary(user_id)

        return {
            "id": user.id,
            "username": user.username,
            "is_channel": user.is_channel,
            "channel_status": user.channel_status,
            "referrer_id": user.referrer_id,
            "bank": bank,
            "commission_summary": ChannelCommissionSummary(
                total_frozen=summary.get("frozen", Decimal("0")),
                total_available=summary.get("available", Decimal("0")),
                total_withdrawn=summary.get("withdrawn", Decimal("0")),
            ),
        }


# ============ 管理员侧 Service ============

class ChannelAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ChannelRepository(db)
        self.user_repo = V1UserRepository(db)

    async def review_application(
        self, app_id: int, admin_id: int, action: str, reject_reason: str | None = None
    ) -> ChannelApplication:
        app = await self.repo.get_application_by_id(app_id)
        if not app:
            raise BizException("申请记录不存在")
        if app.status != "pending":
            raise BizException("该申请已被处理")

        app.status = action  # approved / rejected
        app.reviewed_at = datetime.utcnow()
        app.reviewer_id = admin_id
        if action == "rejected":
            app.reject_reason = reject_reason or "不符合渠道商资质"

        # 更新用户渠道商状态
        user = await self.user_repo.get_by_id(app.user_id)
        if user:
            if action == "approved":
                user.is_channel = True
                user.channel_status = "approved"
                # 自动生成邀请码
                existing_code = await self.repo.get_invite_code_by_channel_id(user.id)
                if not existing_code:
                    code = ChannelInviteCode(
                        channel_id=user.id,
                        invite_code=generate_invite_code(),
                        is_custom=0,
                    )
                    await self.repo.create_invite_code(code)
            else:
                user.channel_status = "rejected"

        await self.repo.update_application(app)
        await self.db.commit()
        return app

    async def list_applications(
        self, status: str | None = None, skip: int = 0, limit: int = 20
    ):
        return await self.repo.list_applications(status, skip, limit)

    async def list_channels(
        self, status: str | None = None, skip: int = 0, limit: int = 20
    ):
        return await self.repo.list_channels(status, skip, limit)

    async def get_commission_setting(self) -> ChannelSetting:
        setting = await self.repo.get_setting()
        if not setting:
            setting = ChannelSetting(l1_rate=Decimal("0.1000"), l2_rate=Decimal("0.0500"))
            return await self.repo.upsert_setting(setting)
        return setting

    async def update_commission_setting(
        self, l1_rate: Decimal, l2_rate: Decimal
    ) -> ChannelSetting:
        if l1_rate < 0 or l1_rate > 1 or l2_rate < 0 or l2_rate > 1:
            raise BizException("佣金比例必须在0-100%之间")
        setting = ChannelSetting(l1_rate=l1_rate, l2_rate=l2_rate)
        return await self.repo.upsert_setting(setting)

    async def review_withdrawal(
        self, withdrawal_id: int, admin_id: int, action: str, reject_reason: str | None = None
    ) -> ChannelWithdrawal:
        withdrawal = await self.repo.get_withdrawal_by_id(withdrawal_id)
        if not withdrawal:
            raise BizException("提现记录不存在")
        if withdrawal.status != "pending":
            raise BizException("该提现申请已被处理")

        withdrawal.status = action  # approved / rejected
        withdrawal.reviewed_at = datetime.utcnow()
        withdrawal.reviewer_id = admin_id
        if action == "rejected":
            withdrawal.reject_reason = reject_reason or "不符合提现条件"
        else:
            # 通过：从可用佣金中扣减实际提现金额
            _, insufficient = await self.repo.deduct_available_commission(withdrawal.channel_id, withdrawal.amount)
            if insufficient > 0:
                raise BizException(f"可用余额不足，无法完成提现，差额为 {insufficient}")

        await self.repo.update_withdrawal(withdrawal)
        return withdrawal

    async def list_withdrawals(
        self, status: str | None = None, skip: int = 0, limit: int = 20
    ):
        return await self.repo.list_withdrawals(status, skip, limit)

    async def get_channel_orders(self, channel_id: int, skip: int = 0, limit: int = 50):
        return await self.repo.get_orders_by_channel(channel_id, skip, limit)


# ============ 佣金计算 Service（供 AOP 切面调用） ============

class CommissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ChannelRepository(db)
        self.user_repo = V1UserRepository(db)

    async def on_order_paid(self, order_id: int, actual_amount: Decimal) -> None:
        """订单支付成功时调用：写入 OrderChannel + 冻结佣金"""
        # 幂等：检查是否已处理
        existing = await self.repo.get_order_channel(order_id)
        if existing:
            return  # 已处理，跳过

        # 查订单对应的用户
        result = await self.db.execute(select(Order.user_id).where(Order.id == order_id))
        order_user_id = result.scalar_one_or_none()
        if not order_user_id:
            return

        order_user = await self.user_repo.get_by_id(order_user_id)
        if not order_user:
            return

        # 追溯 L1 和 L2 渠道商
        l1_channel_id = None
        l2_channel_id = None

        referrer = await self.user_repo.get_by_id(order_user.referrer_id) if order_user.referrer_id else None
        if referrer and referrer.is_channel and referrer.channel_status == "approved":
            l1_channel_id = referrer.id
            # 查上上级
            if referrer.referrer_id:
                l2_referrer = await self.user_repo.get_by_id(referrer.referrer_id)
                if l2_referrer and l2_referrer.is_channel and l2_referrer.channel_status == "approved":
                    l2_channel_id = l2_referrer.id

        order_channel = OrderChannel(
            order_id=order_id,
            l1_channel_id=l1_channel_id,
            l2_channel_id=l2_channel_id,
            actual_amount=actual_amount,
        )
        await self.repo.create_order_channel(order_channel)

        # 冻结佣金
        setting = await self.repo.get_setting()
        if not setting:
            return

        if l1_channel_id:
            # 幂等检查
            existing_comm = await self.repo.get_commission_by_order_and_channel(order_id, l1_channel_id, 1)
            if not existing_comm:
                commission = ChannelCommission(
                    channel_id=l1_channel_id,
                    order_id=order_id,
                    level=1,
                    amount=actual_amount * setting.l1_rate,
                    status="frozen",
                )
                await self.repo.create_commission(commission)

        if l2_channel_id:
            existing_comm = await self.repo.get_commission_by_order_and_channel(order_id, l2_channel_id, 2)
            if not existing_comm:
                commission = ChannelCommission(
                    channel_id=l2_channel_id,
                    order_id=order_id,
                    level=2,
                    amount=actual_amount * setting.l2_rate,
                    status="frozen",
                )
                await self.repo.create_commission(commission)

    async def on_order_completed(self, order_id: int) -> None:
        """订单完成时调用：佣金从 frozen → available"""
        order_channel = await self.repo.get_order_channel(order_id)
        if not order_channel:
            return

        if order_channel.l1_channel_id:
            await self.repo.update_commission_status(order_channel.l1_channel_id, order_id, "available")
        if order_channel.l2_channel_id:
            await self.repo.update_commission_status(order_channel.l2_channel_id, order_id, "available")
