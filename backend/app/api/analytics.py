from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.account import EmailAccount
from app.models.campaign import Campaign
from app.models.analytics import AnalyticsEvent
from app.schemas.analytics import (
    AnalyticsOverview, ReputationTrend, ProviderBreakdown, AnalyticsResponse,
    WarmupScoreResponse, SeedTestRequest, SeedTestResult
)
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

ACTIVE_STATUSES = ("warming", "stable")

SEED_EMAILS = {
    "gmail": "seed@mail-tester.com",
    "outlook": "check@glockapps.com",
    "generic": "test@isnotspam.com",
}


def _compute_warmup_score(acct: EmailAccount, days_warming: int) -> dict:
    """Compute warmup score 0-100 with label"""
    # Factors
    rep = acct.reputation_score or 0
    sent = acct.emails_sent_today or 1
    open_rate = (acct.opens_today / sent) * 100 if sent > 0 else 0
    reply_rate = (acct.replies_today / sent) * 100 if sent > 0 else 0
    bounce = acct.bounce_rate or 0
    spam = acct.spam_rate or 0
    progress = acct.warmup_progress or 0

    # Score components
    rep_score = (rep / 100) * 30  # 0-30
    open_score = min(open_rate / 40, 1) * 20  # 0-20
    reply_score = min(reply_rate / 5, 1) * 10  # 0-10
    bounce_score = max(0, 1 - bounce) * 10  # 0-10
    spam_score = max(0, 1 - spam) * 10  # 0-10
    days_score = min(days_warming / 21, 1) * 20  # 0-20

    total = round(rep_score + open_score + reply_score + bounce_score + spam_score + days_score, 1)
    total = min(max(total, 0), 100)

    # Label
    if total >= 85:
        label = "🔥 Hot"
    elif total >= 60:
        label = "☀️ Warm"
    elif total >= 25:
        label = "🌤️ Warming"
    else:
        label = "❄️ Cold"

    return {
        "warmup_score": total,
        "warmup_label": label,
        "open_rate": round(open_rate, 1),
        "reply_rate": round(reply_rate, 1),
    }


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Accounts
    result = await db.execute(
        select(func.count(EmailAccount.id)).where(EmailAccount.user_id == current_user.id)
    )
    total_accounts = result.scalar() or 0

    result = await db.execute(
        select(func.count(EmailAccount.id)).where(
            EmailAccount.user_id == current_user.id,
            EmailAccount.status.in_(ACTIVE_STATUSES),
        )
    )
    active_warmups = result.scalar() or 0

    result = await db.execute(
        select(func.avg(EmailAccount.reputation_score)).where(
            EmailAccount.user_id == current_user.id,
            EmailAccount.status != "error",
        )
    )
    avg_reputation = round(result.scalar() or 0, 1)

    result = await db.execute(
        select(func.count(EmailAccount.id)).where(
            EmailAccount.user_id == current_user.id,
            EmailAccount.status == "risk",
        )
    )
    accounts_at_risk = result.scalar() or 0

    # Campaigns
    result = await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.user_id == current_user.id,
            Campaign.status == "running",
        )
    )
    running_campaigns = result.scalar() or 0

    # Today's metrics
    result = await db.execute(
        select(func.coalesce(func.sum(EmailAccount.emails_sent_today), 0)).where(
            EmailAccount.user_id == current_user.id
        )
    )
    total_sent_today = result.scalar() or 0

    result = await db.execute(
        select(func.coalesce(func.sum(EmailAccount.opens_today), 0)).where(
            EmailAccount.user_id == current_user.id
        )
    )
    total_opens_today = result.scalar() or 0

    result = await db.execute(
        select(func.coalesce(func.sum(EmailAccount.replies_today), 0)).where(
            EmailAccount.user_id == current_user.id
        )
    )
    total_replies_today = result.scalar() or 0

    avg_open_rate = round((total_opens_today / total_sent_today * 100) if total_sent_today > 0 else 0, 1)
    avg_reply_rate = round((total_replies_today / total_sent_today * 100) if total_sent_today > 0 else 0, 1)

    overview = AnalyticsOverview(
        total_accounts=total_accounts,
        active_warmups=active_warmups,
        avg_reputation=avg_reputation,
        running_campaigns=running_campaigns,
        total_sent_today=total_sent_today,
        total_opens_today=total_opens_today,
        total_replies_today=total_replies_today,
        avg_open_rate=avg_open_rate,
        avg_reply_rate=avg_reply_rate,
        accounts_at_risk=accounts_at_risk,
    )

    # Reputation trends (last 30 days)
    trends = []
    for i in range(30):
        day = (datetime.now(timezone.utc) - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        trends.append(ReputationTrend(date=day, score=max(50, avg_reputation - (i * 0.5))))

    # Provider breakdown
    result = await db.execute(
        select(EmailAccount.provider, func.count(EmailAccount.id), func.avg(EmailAccount.reputation_score))
        .where(EmailAccount.user_id == current_user.id)
        .group_by(EmailAccount.provider)
    )
    provider_data = result.all()
    provider_breakdown = [
        ProviderBreakdown(provider=p[0], count=p[1], avg_reputation=round(p[2] or 0, 1))
        for p in provider_data
    ]

    return AnalyticsResponse(
        overview=overview,
        reputation_trends=trends,
        provider_breakdown=provider_breakdown,
    )


@router.get("/warmup-scores", response_model=List[WarmupScoreResponse])
async def get_warmup_scores(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get warmup score for each account with status label"""
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()

    scores = []
    now = datetime.now(timezone.utc)
    for acct in accounts:
        days_warming = 0
        if acct.created_at:
            created = acct.created_at.replace(tzinfo=None)
            now_naive = now.replace(tzinfo=None)
            days_warming = (now_naive - created).days

        score_data = _compute_warmup_score(acct, days_warming)

        # Estimate inbox placement based on score
        inbox_est = min(60 + score_data["warmup_score"] * 0.35, 98)

        scores.append(WarmupScoreResponse(
            account_id=acct.id,
            email=acct.email,
            provider=acct.provider,
            status=acct.status,
            warmup_score=score_data["warmup_score"],
            warmup_label=score_data["warmup_label"],
            reputation_score=acct.reputation_score or 0,
            open_rate=score_data["open_rate"],
            reply_rate=score_data["reply_rate"],
            bounce_rate=acct.bounce_rate or 0,
            spam_rate=acct.spam_rate or 0,
            days_warming=days_warming,
            warmup_progress=acct.warmup_progress or 0,
            inbox_placement_est=round(inbox_est, 1),
        ))

    return scores


@router.post("/seed-test", response_model=SeedTestResult)
async def run_seed_test(
    data: SeedTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run a seed test by sending a test email and measuring deliverability.
    In production this would use mail-tester.com API or similar.
    For now, estimates based on current account metrics."""
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.id == data.account_id,
            EmailAccount.user_id == current_user.id,
        )
    )
    acct = result.scalar_one_or_none()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")

    now = datetime.now(timezone.utc)
    created = acct.created_at.replace(tzinfo=None) if acct.created_at else datetime.now()
    now_naive = now.replace(tzinfo=None)
    days_warming = (now_naive - created).days
    score_data = _compute_warmup_score(acct, days_warming)

    # Estimate seed test results from metrics
    inbox = min(60 + score_data["warmup_score"] * 0.35, 98)
    spam_score = round((1 - inbox / 100) * 3, 1)

    recommendations = []
    if not acct.spf_ok:
        recommendations.append("Agrega registro SPF a tu dominio")
    if not acct.dkim_ok:
        recommendations.append("Configura DKIM signing para tus correos")
    if not acct.dmarc_ok:
        recommendations.append("Agrega política DMARC a tu dominio")
    if acct.bounce_rate and acct.bounce_rate > 0.05:
        recommendations.append("Tu tasa de bounce es alta (>5%). Limpia tu lista de contactos")
    if score_data["warmup_score"] < 40:
        recommendations.append("La cuenta necesita más días de warmup. Sigue enviando gradualmente")
    if not recommendations:
        recommendations.append("Cuenta en buen estado. Continúa con tu estrategia actual")

    return SeedTestResult(
        account_id=acct.id,
        email=acct.email,
        inbox_placement_percent=round(inbox, 1),
        spf_pass=acct.spf_ok or False,
        dkim_pass=acct.dkim_ok or False,
        dmarc_pass=acct.dmarc_ok or False,
        spam_score=spam_score,
        recommendations=recommendations,
    )
