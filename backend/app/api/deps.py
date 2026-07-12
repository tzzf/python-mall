from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.user_service import V1UserService, AdminUserService
from app.core.config import settings
import jwt

oauth2_scheme_v1 = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="/api/admin/users/login")


async def get_current_v1_user(
    token: str = Depends(oauth2_scheme_v1),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的 Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的 Token")

    svc = V1UserService(db)
    user = await svc.get_user(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


async def get_current_admin(
    token: str = Depends(oauth2_scheme_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("type")
        if user_id is None or user_type != "admin":
            raise HTTPException(status_code=401, detail="无效的 Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的 Token")

    svc = AdminUserService(db)
    admin = await svc.get_admin(int(user_id))
    if admin is None:
        raise HTTPException(status_code=401, detail="管理员不存在")
    return admin
