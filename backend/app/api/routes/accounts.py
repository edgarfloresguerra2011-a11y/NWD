from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import EmailAccount, User
from app.schemas.schemas import EmailAccountCreate, EmailAccountOut

router = APIRouter(prefix="/accounts", tags=["email-accounts"])


@router.get("/", response_model=list[EmailAccountOut])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=EmailAccountOut, status_code=201)
async def create_account(
    data: EmailAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = EmailAccount(**data.model_dump(), user_id=current_user.id)
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


@router.patch("/{account_id}/warmup", response_model=EmailAccountOut)
async def toggle_warmup(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.id == uuid.UUID(account_id),
            EmailAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    account.warmup_enabled = not account.warmup_enabled
    await db.flush()
    await db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.id == uuid.UUID(account_id),
            EmailAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    await db.delete(account)
