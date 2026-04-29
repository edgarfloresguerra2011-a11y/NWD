from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.account import EmailAccount
from app.schemas.account import AccountConnect, AccountResponse, AccountUpdate, AccountWarmupSchedule
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def connect_account(
    data: AccountConnect,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    provider = data.provider.lower()
    if provider not in ("gmail", "outlook", "smtp"):
        raise HTTPException(status_code=400, detail="Provider must be gmail, outlook, or smtp")

    account = EmailAccount(
        user_id=current_user.id,
        email=data.email,
        provider=provider,
        status="connecting",
        access_token=data.access_token,
        refresh_token=data.refresh_token,
        smtp_host=data.smtp_host,
        smtp_port=data.smtp_port,
        imap_host=data.imap_host,
        imap_port=data.imap_port,
        smtp_username=data.smtp_username,
        smtp_password=data.smtp_password,
        warmup_max_per_day=data.warmup_max_per_day or 50,
        warmup_reply_rate=data.warmup_reply_rate or 0.05,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()
    return [AccountResponse.model_validate(a) for a in accounts]


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
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
    return AccountResponse.model_validate(account)


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.id == account_id, EmailAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    if data.warmup_max_per_day is not None:
        account.warmup_max_per_day = data.warmup_max_per_day
    if data.warmup_reply_rate is not None:
        account.warmup_reply_rate = data.warmup_reply_rate
    if data.smtp_password is not None:
        account.smtp_password = data.smtp_password

    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
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
    await db.delete(account)
    await db.commit()


@router.post("/{account_id}/start-warmup", response_model=AccountResponse)
async def start_warmup(
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

    account.status = "warming"
    account.warmup_progress = 0.0
    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)


@router.post("/{account_id}/pause-warmup", response_model=AccountResponse)
async def pause_warmup(
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

    account.status = "paused"
    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)


@router.post("/{account_id}/adjust-warmup", response_model=AccountResponse)
async def adjust_warmup(
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
    await db.refresh(account)
    return AccountResponse.model_validate(account)
