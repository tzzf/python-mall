from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repo import V1UserRepository, AdminUserRepository
from app.models.user import V1User, AdminUser
from app.schemas.user import V1UserCreate, AdminUserCreate, AdminUserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional
from datetime import datetime, timedelta
import jwt
from app.core.config import settings


class V1UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = V1UserRepository(db)

    def create_user(self, user_in: V1UserCreate, referrer_id: int | None = None) -> V1User:
        hashed_pwd = get_password_hash(user_in.password)
        user = V1User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_pwd,
            referrer_id=referrer_id,
        )
        return self.repo.create(user)

    async def verify_login(self, username: str, password: str) -> Optional[V1User]:
        user = await self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_user(self, user_id: int) -> Optional[V1User]:
        return await self.repo.get_by_id(user_id)


class AdminUserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdminUserRepository(db)

    async def create_admin(self, admin_in: AdminUserCreate) -> AdminUser:
        hashed_pwd = get_password_hash(admin_in.password)
        admin = AdminUser(
            username=admin_in.username,
            email=admin_in.email,
            hashed_password=hashed_pwd,
        )
        return await self.repo.create(admin)

    async def verify_login(self, username: str, password: str) -> Optional[AdminUser]:
        admin = await self.repo.get_by_username(username)
        if not admin:
            return None
        if not verify_password(password, admin.hashed_password):
            return None
        return admin

    def create_access_token(self, admin_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(admin_id), "type": "admin", "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_admin(self, admin_id: int) -> Optional[AdminUser]:
        return await self.repo.get_by_id(admin_id)

    async def get_admins(self, skip: int = 0, limit: int = 100):
        return await self.repo.get_all(skip=skip, limit=limit)

    async def update_admin(self, admin_id: int, admin_in: AdminUserUpdate) -> Optional[AdminUser]:
        admin = await self.repo.get_by_id(admin_id)
        if not admin:
            return None
        for field, value in admin_in.model_dump(exclude_unset=True).items():
            setattr(admin, field, value)
        return await self.repo.update(admin)
    
    async def change_password(self, admin_id: int, old_password: str, new_password: str):
        admin = await self.repo.get_by_id(admin_id)
        if not admin:
            raise ValueError("管理员不存在")
        if not verify_password(old_password, admin.hashed_password):
            raise ValueError("原密码错误")
        new_hashed = get_password_hash(new_password)
        await self.repo.update_password(admin_id, new_hashed)
        return {"message": "密码修改成功"}

