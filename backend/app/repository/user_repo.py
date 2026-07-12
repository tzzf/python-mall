from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import V1User, AdminUser
from typing import Optional, List

class V1UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[V1User]:
        result = await self.db.execute(select(V1User).where(V1User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[V1User]:
        result = await self.db.execute(select(V1User).where(V1User.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[V1User]:
        result = await self.db.execute(select(V1User).where(V1User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: V1User) -> V1User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


class AdminUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[AdminUser]:
        result = await self.db.execute(select(AdminUser).where(AdminUser.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[AdminUser]:
        result = await self.db.execute(select(AdminUser).where(AdminUser.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[AdminUser]:
        result = await self.db.execute(select(AdminUser).where(AdminUser.email == email))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AdminUser]:
        result = await self.db.execute(select(AdminUser).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, user: AdminUser) -> AdminUser:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: AdminUser) -> AdminUser:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: AdminUser) -> None:
        await self.db.delete(user)
        await self.db.commit()

    async def update_password(self, admin_id: int, new_hashed_password: str) -> bool:
        from sqlalchemy import update
        result = await self.db.execute(
            update(AdminUser)
            .where(AdminUser.id == admin_id)
            .values(hashed_password=new_hashed_password)
        )
        await self.db.commit()
        return result.rowcount > 0

