from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    company: Optional[str]
    is_active: bool
    is_verified: bool
    plan_tier: str
    whitelabel_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
