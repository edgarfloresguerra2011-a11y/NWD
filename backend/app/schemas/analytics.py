from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalyticsOverview(BaseModel):
    total_accounts: int
    active_warmups: int
    avg_reputation: float
    running_campaigns: int
    total_sent_today: int
    total_opens_today: int
    total_replies_today: int
    avg_open_rate: float
    avg_reply_rate: float
    accounts_at_risk: int


class ReputationTrend(BaseModel):
    date: str
    score: float


class ProviderBreakdown(BaseModel):
    provider: str
    count: int
    avg_reputation: float


class AnalyticsResponse(BaseModel):
    overview: AnalyticsOverview
    reputation_trends: List[ReputationTrend]
    provider_breakdown: List[ProviderBreakdown]


class WarmupScoreResponse(BaseModel):
    account_id: int
    email: str
    provider: str
    status: str
    warmup_score: float  # 0-100
    warmup_label: str  # ❄️ Cold | 🌤️ Warming | ☀️ Warm | 🔥 Hot
    reputation_score: float
    open_rate: float
    reply_rate: float
    bounce_rate: float
    spam_rate: float
    days_warming: int
    warmup_progress: float
    inbox_placement_est: float  # estimated inbox placement %


class SeedTestRequest(BaseModel):
    account_id: int
    test_email: str  # email to send test to (e.g. test@mail-tester.com)


class SeedTestResult(BaseModel):
    account_id: int
    email: str
    inbox_placement_percent: float
    spf_pass: bool
    dkim_pass: bool
    dmarc_pass: bool
    spam_score: float
    recommendations: List[str]


class DNSCheckResult(BaseModel):
    domain: str
    spf: Dict[str, Any]
    dkim: Dict[str, Any]
    dmarc: Dict[str, Any]
    overall_ok: bool


class DomainCreate(BaseModel):
    domain_name: str


class DomainResponse(BaseModel):
    id: int
    domain_name: str
    spf_status: str
    dkim_status: str
    dmarc_status: str
    overall_ok: bool
    spf_record: Optional[str] = None
    dkim_record: Optional[str] = None
    dmarc_record: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
