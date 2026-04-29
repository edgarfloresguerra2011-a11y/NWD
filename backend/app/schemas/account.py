from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class AccountConnect(BaseModel):
    email: EmailStr
    provider: str  # gmail, outlook, smtp
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    warmup_max_per_day: Optional[int] = 50
    warmup_reply_rate: Optional[float] = 0.05


class AccountResponse(BaseModel):
    id: int
    email: str
    provider: str
    status: str
    warmup_progress: float
    reputation_score: float
    emails_sent_today: int
    emails_received_today: int
    opens_today: int
    replies_today: int
    bounce_rate: float
    spam_rate: float
    spf_ok: bool
    dkim_ok: bool
    dmarc_ok: bool
    warmup_max_per_day: int
    warmup_reply_rate: float
    last_warmup_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountUpdate(BaseModel):
    warmup_max_per_day: Optional[int] = None
    warmup_reply_rate: Optional[float] = None
    smtp_password: Optional[str] = None


class AccountWarmupSchedule(BaseModel):
    max_per_day: Optional[int] = None
    reply_rate: Optional[float] = None
    ramp_days: Optional[int] = None
