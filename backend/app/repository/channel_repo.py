from app.core.pagination.filters.order_channel import OrderChannelFilter
from app.core.pagination.filters.channel_commission import ChannelCommissionFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, literal
from app.models.channel import (
    ChannelInviteCode,
    ChannelApplication,
    ChannelBank,
    ChannelCommission,
    ChannelWithdrawal,
    ChannelSetting,
    OrderChannel,
)
from app.models.user import V1User
from app.core.pagination import paginate, PaginatedResult
from app.core.pagination.filters.user import V1UserFilter
from app.core.pagination.filters.channel import ChannelApplicationFilter, ChannelWithdrawalFilter
from typing import Optional, List
from decimal import Decimal


class ChannelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============ 邀请码 ============

    async def get_invite_code_by_code(self, code: str) -> Optional[ChannelInviteCode]:
        result = await self.db.execute(
            select(ChannelInviteCode).where(ChannelInviteCode.invite_code == code)
        )
        return result.scalar_one_or_none()

    async def get_invite_code_by_channel_id(self, channel_id: int) -> Optional[ChannelInviteCode]:
        result = await self.db.execute(
            select(ChannelInviteCode).where(ChannelInviteCode.channel_id == channel_id)
        )
        return result.scalar_one_or_none()

    async def create_invite_code(self, invite_code: ChannelInviteCode) -> ChannelInviteCode:
        self.db.add(invite_code)
        await self.db.commit()
        await self.db.refresh(invite_code)
        return invite_code

    async def update_invite_code(self, invite_code: ChannelInviteCode) -> ChannelInviteCode:
        await self.db.commit()
        await self.db.refresh(invite_code)
        return invite_code

    async def is_invite_code_used_by_others(self, code: str, exclude_channel_id: int) -> bool:
        result = await self.db.execute(
            select(ChannelInviteCode).where(
                and_(
                    ChannelInviteCode.invite_code == code,
                    ChannelInviteCode.channel_id != exclude_channel_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    # ============ 申请 ============

    async def get_application_by_user_id(self, user_id: int) -> Optional[ChannelApplication]:
        result = await self.db.execute(
            select(ChannelApplication).where(ChannelApplication.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_application(self, application: ChannelApplication) -> ChannelApplication:
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def get_application_by_id(self, app_id: int) -> Optional[ChannelApplication]:
        result = await self.db.execute(
            select(ChannelApplication).where(ChannelApplication.id == app_id)
        )
        return result.scalar_one_or_none()

    async def update_application(self, application: ChannelApplication) -> ChannelApplication:
        from sqlalchemy import update
        await self.db.execute(
            update(ChannelApplication).where(
                ChannelApplication.user_id == application.user_id
            ).values(status=application.status)
        )
        await self.db.commit()
        return application

    async def list_applications(self, status: Optional[str] = None, skip: int = 0, limit: int = 20) -> PaginatedResult[ChannelApplication]:
        filters = ChannelApplicationFilter(status=status)
        return await paginate(self.db, ChannelApplication, filters, skip=skip, limit=limit)

    # ============ 银行卡 ============

    async def get_bank_by_channel_id(self, channel_id: int) -> Optional[ChannelBank]:
        result = await self.db.execute(
            select(ChannelBank).where(ChannelBank.channel_id == channel_id)
        )
        return result.scalar_one_or_none()

    async def upsert_bank(self, bank: ChannelBank) -> ChannelBank:
        existing = await self.get_bank_by_channel_id(bank.channel_id)
        if existing:
            existing.bank_name = bank.bank_name
            existing.bank_account = bank.bank_account
            existing.account_holder = bank.account_holder
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            self.db.add(bank)
            await self.db.commit()
            await self.db.refresh(bank)
            return bank

    # ============ 佣金 ============

    async def get_commission_by_order_and_channel(
        self, order_id: int, channel_id: int, level: int
    ) -> Optional[ChannelCommission]:
        result = await self.db.execute(
            select(ChannelCommission).where(
                and_(
                    ChannelCommission.order_id == order_id,
                    ChannelCommission.channel_id == channel_id,
                    ChannelCommission.level == level,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_commissions_by_channel(
        self, channel_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 50
    ):
        filters = ChannelCommissionFilter(
            channel_id=channel_id,
            status=status
        )
        return await paginate(self.db, ChannelCommission, filters, skip=skip, limit=limit) 
        count_query = select(func.count(ChannelCommission.id)).where(ChannelCommission.channel_id == channel_id)
        if status:
            count_query = count_query.where(ChannelCommission.status == status)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = select(ChannelCommission).where(ChannelCommission.channel_id == channel_id)
        if status:
            query = query.where(ChannelCommission.status == status)
        query = query.order_by(ChannelCommission.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_commission_summary(self, channel_id: int) -> dict:
        result = await self.db.execute(
            select(
                ChannelCommission.status,
                func.coalesce(func.sum(ChannelCommission.balance), Decimal("0")),
                func.coalesce(func.sum(ChannelCommission.amount), Decimal("0")),
            )
            .where(ChannelCommission.channel_id == channel_id)
            .group_by(ChannelCommission.status)
        )
        rows = result.all()
        summary = {"frozen": Decimal("0"), "available": Decimal("0"), "withdrawn": Decimal("0")}
        for status, balance_sum, amount_sum in rows:
            if status == "frozen":
                summary["frozen"] += amount_sum
            elif status == "available":
                summary["available"] += balance_sum
                summary["withdrawn"] += amount_sum - balance_sum
            elif status == "withdrawn":
                # withdrawn 记录的 balance 已是 0，用 amount 填充已提现金额
                summary["withdrawn"] += amount_sum
        return summary

    async def create_commission(self, commission: ChannelCommission) -> ChannelCommission:
        commission.balance = commission.amount  # 初始可用余额等于佣金总额
        self.db.add(commission)
        await self.db.commit()
        await self.db.refresh(commission)
        return commission

    async def update_commission_status(
        self, channel_id: int, order_id: int, new_status: str
    ) -> None:
        from sqlalchemy import update
        await self.db.execute(
            update(ChannelCommission).where(
                and_(
                    ChannelCommission.channel_id == channel_id,
                    ChannelCommission.order_id == order_id,
                )
            ).values(status=new_status)
        )
        await self.db.commit()

    async def deduct_available_commission(
        self, channel_id: int, amount: Decimal
    ) -> tuple[Decimal, Decimal]:
        """
        从可用佣金中扣减指定金额，按时间顺序从最早的记录开始扣。
        扣减的是每条记录的 balance（可用余额），amount（佣金本金）不变。
        当 balance 扣至 0 时整条标记为 withdrawn。

        返回 (实际扣减金额, 可用余额不足部分的金额)。
        余额不足时 returned[1] > 0，调用方负责判断并处理。
        """
        from sqlalchemy import update

        remaining = amount
        # 查出所有可用佣金，按创建时间正序（加 FOR UPDATE 防止并发）
        result = await self.db.execute(
            select(ChannelCommission)
            .where(
                and_(
                    ChannelCommission.channel_id == channel_id,
                    ChannelCommission.status == "available",
                    ChannelCommission.balance > 0,
                )
            )
            .order_by(ChannelCommission.created_at.asc())
            .with_for_update()
        )
        commissions = list(result.scalars().all())

        total_available = sum(comm.balance for comm in commissions)
        if total_available < amount:
            return (Decimal("0"), amount - total_available)

        for comm in commissions:
            if remaining <= 0:
                break
            if comm.balance <= remaining:
                # 这条记录余额全部扣完
                remaining -= comm.balance
                await self.db.execute(
                    update(ChannelCommission)
                    .where(ChannelCommission.id == comm.id)
                    .values(balance=Decimal("0"), status="withdrawn")
                )
            else:
                # 部分扣：balance 减少，status 保持 available
                deducted = remaining
                remaining = Decimal("0")
                await self.db.execute(
                    update(ChannelCommission)
                    .where(ChannelCommission.id == comm.id)
                    .values(balance=comm.balance - deducted)
                )

        await self.db.commit()
        return (amount - remaining, Decimal("0"))

    # ============ 提现 ============

    async def create_withdrawal(self, withdrawal: ChannelWithdrawal) -> ChannelWithdrawal:
        self.db.add(withdrawal)
        await self.db.commit()
        await self.db.refresh(withdrawal)
        return withdrawal

    async def get_withdrawal_by_id(self, withdrawal_id: int) -> Optional[ChannelWithdrawal]:
        result = await self.db.execute(
            select(ChannelWithdrawal).where(ChannelWithdrawal.id == withdrawal_id)
        )
        return result.scalar_one_or_none()

    async def list_withdrawals(
        self, status: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> PaginatedResult[ChannelWithdrawal]:
        filters = ChannelWithdrawalFilter(status=status)
        return await paginate(self.db, ChannelWithdrawal, filters, skip=skip, limit=limit)

    async def update_withdrawal(self, withdrawal: ChannelWithdrawal) -> ChannelWithdrawal:
        await self.db.commit()
        await self.db.refresh(withdrawal)
        return withdrawal

    # ============ 佣金设置 ============

    async def get_setting(self) -> Optional[ChannelSetting]:
        result = await self.db.execute(select(ChannelSetting))
        return result.scalar_one_or_none()

    async def upsert_setting(self, setting: ChannelSetting) -> ChannelSetting:
        existing = await self.get_setting()
        if existing:
            existing.l1_rate = setting.l1_rate
            existing.l2_rate = setting.l2_rate
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            self.db.add(setting)
            await self.db.commit()
            await self.db.refresh(setting)
            return setting

    # ============ 订单渠道关系 ============

    async def get_order_channel(self, order_id: int) -> Optional[OrderChannel]:
        result = await self.db.execute(
            select(OrderChannel).where(OrderChannel.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def create_order_channel(self, order_channel: OrderChannel) -> OrderChannel:
        self.db.add(order_channel)
        await self.db.commit()
        await self.db.refresh(order_channel)
        return order_channel

    async def get_orders_by_channel(self, channel_id: int, skip: int = 0, limit: int = 50) -> PaginatedResult[OrderChannel]:
        filters = OrderChannelFilter(channel_id=channel_id)
        return await paginate(self.db, OrderChannel, filters, skip=skip, limit=limit)

    # ============ 渠道商列表 ============

    async def list_channels(
        self, status: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> PaginatedResult[V1User]:
        filters = V1UserFilter(
            status=status,
            is_channel=True,
        )
        return await paginate(self.db, V1User, filters, skip=skip, limit=limit)

    # ============ 下级查询 ============

    async def get_l1_referrals(self, channel_id: int) -> List[V1User]:
        result = await self.db.execute(
            select(V1User).where(V1User.referrer_id == channel_id)
        )
        return list(result.scalars().all())

    async def get_l2_referrals(self, channel_id: int) -> List[V1User]:
        """查我的下级的下级"""
        # 先查 L1
        l1_ids = [u.id for u in await self.get_l1_referrals(channel_id)]
        if not l1_ids:
            return []
        result = await self.db.execute(
            select(V1User).where(V1User.referrer_id.in_(l1_ids))
        )
        return list(result.scalars().all())
