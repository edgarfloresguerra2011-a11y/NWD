import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ─── Auth ───────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─── User ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── EmailAccount ────────────────────────────────────────────────────────────

class EmailAccountCreate(BaseModel):
    email: EmailStr
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    daily_limit: int = 20


class EmailAccountOut(BaseModel):
    id: uuid.UUID
    email: str
    smtp_host: str
    smtp_port: int
    is_active: bool
    warmup_enabled: bool
    daily_limit: int
    emails_sent_today: int
    reputation_score: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Campaign ────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    subject: str
    body: str
    daily_limit: int = 50


class CampaignOut(BaseModel):
    id: uuid.UUID
    name: str
    subject: str
    status: str
    daily_limit: int
    emails_sent: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipientAdd(BaseModel):
    email: EmailStr
    name: Optional[str] = None
