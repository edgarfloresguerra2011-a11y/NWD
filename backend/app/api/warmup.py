from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.account import EmailAccount
from app.schemas.account import AccountResponse, AccountWarmupSchedule
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/warmup", tags=["Warmup"])


@router.get("/status")
async def get_warmup_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()

    return {
        "total_accounts": len(accounts),
        "warming": sum(1 for a in accounts if a.status == "warming"),
        "stable": sum(1 for a in accounts if a.status == "stable"),
        "paused": sum(1 for a in accounts if a.status == "paused"),
        "risk": sum(1 for a in accounts if a.status == "risk"),
        "error": sum(1 for a in accounts if a.status == "error"),
        "avg_reputation": round(sum(a.reputation_score for a in accounts) / len(accounts), 1) if accounts else 0,
    }


@router.get("/{account_id}/schedule")
async def get_warmup_schedule(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.id == account_id, EmailAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    import math
    schedule = []
    for day in range(1, account.warmup_ramp_days + 1):
        daily_max = min(int(3 * math.pow(1.15, day - 1)), account.warmup_max_per_day)
        schedule.append({
            "day": day,
            "max_emails": daily_max,
            "target_opens": max(1, int(daily_max * 0.3)),
            "target_replies": max(1, int(daily_max * account.warmup_reply_rate)),
        })

    return {
        "account_email": account.email,
        "current_progress": account.warmup_progress,
        "current_status": account.status,
        "schedule": schedule,
    }


@router.put("/{account_id}/schedule")
async def update_warmup_schedule(
    account_id: int,
    data: AccountWarmupSchedule,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.id == account_id, EmailAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    if data.max_per_day is not None:
        account.warmup_max_per_day = data.max_per_day
    if data.reply_rate is not None:
        account.warmup_reply_rate = data.reply_rate
    if data.ramp_days is not None:
        account.warmup_ramp_days = data.ramp_days

    await db.commit()
    return {"message": "Schedule actualizado correctamente", "max_per_day": account.warmup_max_per_day}

@router.post("/{account_id}/trigger")
async def trigger_warmup_cycle(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a manual warmup cycle for an account"""
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.id == account_id, EmailAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    from app.tasks import run_warmup_for_account
    run_warmup_for_account.delay(account_id)
    
    return {"message": "Warmup cycle queued in Celery", "account_id": account_id}

@router.post("/webhook/bounce")
async def bounce_webhook(payload: dict, db: AsyncSession = Depends(get_db)):
    """Placeholder for external bounce/spam webhooks (SendGrid, Mailgun, etc.)"""
    # Logic to identify account and update bounce_rate
    # For now, just log the receipt
    print(f"Received webhook: {payload}")
    return {"status": "received"}
