from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.user_service import AdminUserService
from app.schemas.user import (
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
    TokenResponse,
    LoginRequest,
)
from app.api.deps import get_current_admin
from app.models.user import AdminUser
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/users", tags=["管理端-用户"])

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ChangePasswordResponse(BaseModel):
    message: str

@router.post("/register", response_model=AdminUserResponse, status_code=201)
async def register(admin_in: AdminUserCreate, db: AsyncSession = Depends(get_db)):
    svc = AdminUserService(db)
    existing = await svc.repo.get_by_username(admin_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    existing_email = await svc.repo.get_by_email(admin_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    return await svc.create_admin(admin_in)

@router.post("/login", response_model=TokenResponse)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    svc = AdminUserService(db)
    admin = await svc.verify_login(login_in.username, login_in.password)
    if not admin:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = svc.create_access_token(admin.id)
    return TokenResponse(access_token=token, token_type="bearer")

@router.get("/", response_model=List[AdminUserResponse])
async def list_admins(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    svc = AdminUserService(db)
    return await svc.get_admins(skip=skip, limit=limit)

@router.put("/{admin_id}", response_model=AdminUserResponse)
async def update_admin(
    admin_id: int,
    admin_in: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    svc = AdminUserService(db)
    admin = await svc.update_admin(admin_id, admin_in)
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    return admin

@router.delete("/{admin_id}", status_code=204)
async def delete_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    svc = AdminUserService(db)
    admin = await svc.repo.get_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    await svc.repo.delete(admin)

@router.put("/{admin_id}/password", response_model=ChangePasswordResponse)
async def change_password(
    admin_id: int,
    password_in: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    if current_admin.id != admin_id:
        raise HTTPException(status_code=403, detail="无权修改他人密码")
    svc = AdminUserService(db)
    try:
        return await svc.change_password(admin_id, password_in.old_password, password_in.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
