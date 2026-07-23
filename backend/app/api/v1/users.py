from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.user_service import V1UserService
from app.schemas.user import V1UserCreate, V1UserResponse, TokenResponse, V1UserLogin
from app.api.deps import get_current_v1_user
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["用户端"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


@router.post("/register", response_model=V1UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: V1UserCreate,
    invite_code: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = V1UserService(db)
    existing = await svc.repo.get_by_username(user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    existing_email = await svc.repo.get_by_email(user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")

    # 处理邀请码：查出对应的 referrer_id
    referrer_id = None
    if invite_code:
        from app.repository.channel_repo import ChannelRepository
        channel_repo = ChannelRepository(db)
        invite_record = await channel_repo.get_invite_code_by_code(invite_code.upper())
        if not invite_record:
            raise HTTPException(status_code=400, detail="无效的邀请码")
        referrer_id = invite_record.channel_id

    user = await svc.create_user(user_in, referrer_id=referrer_id)

    # 自己不能是自己的下级（注册后检查）
    if user.referrer_id == user.id:
        user.referrer_id = None
        await db.commit()
    return user


@router.post("/login", response_model=TokenResponse)
async def login(login_in: V1UserLogin, db: AsyncSession = Depends(get_db)):
    svc = V1UserService(db)
    user = await svc.verify_login(login_in.username, login_in.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = svc.create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=V1UserResponse)
async def get_me(current_user = Depends(get_current_v1_user)):
    return current_user
