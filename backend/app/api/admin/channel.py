from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.channel_service import ChannelAdminService
from app.schemas.channel import (
    ChannelApplicationItem,
    ChannelApplicationReviewRequest,
    ChannelListItem,
    ChannelSettingUpdate,
    ChannelSettingResponse,
    WithdrawalReviewRequest,
    WithdrawalListItem,
    ChannelOrderDetail,
    PaginatedResponse,
)
from app.api.deps import get_current_admin
from app.models.user import AdminUser

router = APIRouter(prefix="/channel", tags=["渠道商管理"])


# ============ 申请管理 ============

@router.get("/applications")
async def list_applications(
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    _: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    result = await svc.list_applications(status, skip, limit)
    data = [
        ChannelApplicationItem(
            id=app.id,
            user_id=app.user_id,
            username=username,
            status=app.status,
            created_at=app.created_at,
            reviewed_at=app.reviewed_at,
            reject_reason=app.reject_reason,
        )
        for app, username in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, skip=skip, limit=limit)


@router.put("/applications/{app_id}/review")
async def review_application(
    app_id: int,
    req: ChannelApplicationReviewRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    app = await svc.review_application(app_id, current_admin.id, req.action, req.reject_reason)
    return {"message": f"申请已{('通过' if req.action == 'approved' else '拒绝')}"}


# ============ 渠道商列表 ============

@router.get("/list")
async def list_channels(
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    _: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    result = await svc.list_channels(status, skip, limit)
    data = [
        ChannelListItem(
            id=c.id,
            username=c.username,
            is_channel=c.is_channel,
            channel_status=c.channel_status,
            referrer_id=c.referrer_id,
            created_at=c.created_at,
        )
        for c in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, skip=skip, page=result.page, limit=result.page_size)


# ============ 佣金设置 ============

@router.get("/setting", response_model=ChannelSettingResponse)
async def get_commission_setting(
    _: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    setting = await svc.get_commission_setting()
    return setting


@router.put("/setting", response_model=ChannelSettingResponse)
async def update_commission_setting(
    req: ChannelSettingUpdate,
    _: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    setting = await svc.update_commission_setting(req.l1_rate, req.l2_rate)
    return setting


# ============ 提现管理 ============

@router.get("/withdrawals")
async def list_withdrawals(
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    _: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    result = await svc.list_withdrawals(status, skip, limit)
    data = [
        WithdrawalListItem(
            id=w.id,
            channel_id=w.channel_id,
            username=username,
            amount=w.amount,
            status=w.status,
            created_at=w.created_at,
            reviewed_at=w.reviewed_at,
            reject_reason=w.reject_reason,
        )
        for w, username in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, skip=skip, page=result.page, limit=result.page_size)


@router.put("/withdrawals/{withdrawal_id}/review")
async def review_withdrawal(
    withdrawal_id: int,
    req: WithdrawalReviewRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    w = await svc.review_withdrawal(withdrawal_id, current_admin.id, req.action, req.reject_reason)
    return {"message": f"提现申请已{('通过' if req.action == 'approved' else '拒绝')}"}


# ============ 渠道商订单明细 ============

@router.get("/orders/{channel_id}")
async def get_channel_orders(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    _: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelAdminService(db)
    result = await svc.get_channel_orders(channel_id, skip, limit)
    data = [
        ChannelOrderDetail(
            order_id=oc.order_id,
            actual_amount=oc.actual_amount,
            l1_amount=None,  # 可按需从佣金表查
            l2_amount=None,
            order_created_at=oc.created_at,
        )
        for oc in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, skip=skip, page=result.page, limit=result.page_size)
