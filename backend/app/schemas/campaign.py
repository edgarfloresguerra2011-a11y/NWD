from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class CampaignStepCreate(BaseModel):
    step_order: int
    action: str = "send_email"
    subject: Optional[str] = None
    body_text: Optional[str] = None
    delay_hours: int = 24
    condition_field: Optional[str] = None
    condition_value: Optional[str] = None


class CampaignStepResponse(BaseModel):
    id: int
    campaign_id: int
    step_order: int
    action: str
    subject: Optional[str] = None
    delay_hours: int
    condition_field: Optional[str] = None
    condition_value: Optional[str] = None

    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    name: str
    steps: List[CampaignStepCreate] = []


class CampaignResponse(BaseModel):
    id: int
    user_id: int
    name: str
    status: str
    total_emails: int
    sent_count: int
    open_count: int
    reply_count: int
    bounce_count: int
    spam_count: int
    open_rate: float = 0.0
    reply_rate: float = 0.0
    steps: List[CampaignStepResponse] = []
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    steps: Optional[List[CampaignStepCreate]] = None
