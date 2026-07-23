from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.channel_service import ChannelService
from app.schemas.channel import (
    InviteCodeResponse,
    ChannelApplyResponse,
    ChannelBankCreate,
    ChannelBankResponse,
    ChannelCommissionResponse,
    ChannelCommissionSummary,
    WithdrawalRequest,
    WithdrawalResponse,
    ChannelProfileResponse,
    MyReferralsResponse,
    ReferralUserInfo,
    PaginatedResponse,
)
from app.api.deps import get_current_v1_user
from app.models.user import V1User
from decimal import Decimal

router = APIRouter(prefix="/channel", tags=["渠道商"])


@router.get("/profile", response_model=ChannelProfileResponse)
async def get_my_profile(
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    profile = await svc.get_my_profile(current_user.id)
    return profile


@router.post("/apply", response_model=ChannelApplyResponse)
async def apply_to_be_channel(
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    result = await svc.apply_to_be_channel(current_user.id)
    return result


@router.get("/invite-code", response_model=InviteCodeResponse)
async def get_my_invite_code(
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    code = await svc.get_my_invite_code(current_user.id)
    return InviteCodeResponse(invite_code=code.invite_code, is_custom=bool(code.is_custom))


@router.put("/invite-code")
async def set_custom_invite_code(
    code: str,
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    updated = await svc.set_custom_invite_code(current_user.id, code)
    return {"invite_code": updated.invite_code, "is_custom": bool(updated.is_custom)}


@router.get("/bank", response_model=ChannelBankResponse | None)
async def get_my_bank(
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    bank = await svc.get_my_bank(current_user.id)
    if not bank:
        return None
    return bank


@router.post("/bank", response_model=ChannelBankResponse)
async def save_my_bank(
    bank_in: ChannelBankCreate,
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    bank = await svc.save_my_bank(current_user.id, bank_in)
    return bank


@router.get("/commissions")
async def get_my_commissions(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    result = await svc.get_my_commissions(current_user.id, status, skip, limit)
    data = [
        ChannelCommissionResponse.model_validate(c, from_attributes=True)
        for c in result.items
    ]
    return PaginatedResponse(data=data, total=result.total, page=result.page, skip=skip, limit=limit)


@router.get("/commissions/summary", response_model=ChannelCommissionSummary)
async def get_my_commission_summary(
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    return await svc.get_my_commission_summary(current_user.id)


@router.post("/withdraw", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def apply_withdrawal(
    req: WithdrawalRequest,
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    withdrawal = await svc.apply_withdrawal(current_user.id, req.amount)
    return withdrawal


@router.get("/referrals", response_model=MyReferralsResponse)
async def get_my_referrals(
    current_user: V1User = Depends(get_current_v1_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ChannelService(db)
    result = await svc.get_my_referrals(current_user.id)
    return MyReferralsResponse(
        l1_referrals=[ReferralUserInfo.model_validate(u) for u in result["l1_referrals"]],
        l2_referrals=[ReferralUserInfo.model_validate(u) for u in result["l2_referrals"]],
    )
