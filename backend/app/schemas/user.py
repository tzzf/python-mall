from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import datetime, timezone, timedelta

# === v1 用户端 Schema ===

class V1UserBase(BaseModel):
    username: str
    email: EmailStr

class V1UserCreate(V1UserBase):
    password: str

class V1UserLogin(BaseModel):
    username: str
    password: str

class V1UserResponse(V1UserBase):
    id: int
    is_active: bool
    created_at: datetime
    is_channel: Optional[bool] = None

    class Config:
        from_attributes = True


# === admin 管理端 Schema ===

class AdminUserBase(BaseModel):
    username: str
    email: EmailStr

class AdminUserCreate(AdminUserBase):
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class AdminUserResponse(AdminUserBase):
    id: int
    is_active: bool
    created_at: datetime

    @field_serializer("created_at")
    def convert_to_beijing(self, created_at: datetime) -> str:
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = created_at.replace(tzinfo=timezone.utc).astimezone(beijing_tz)
        return beijing_time.isoformat()

    class Config:
        from_attributes = True


# === Token ===

class TokenResponse(BaseModel):
    code: int = 200
    message: str = "success"
    access_token: str
    token_type: str = "bearer"
