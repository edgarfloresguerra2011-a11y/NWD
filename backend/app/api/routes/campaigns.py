import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Campaign, CampaignRecipient, User
from app.schemas.schemas import CampaignCreate, CampaignOut, RecipientAdd

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignOut])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=CampaignOut, status_code=201)
async def create_campaign(
    data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = Campaign(**data.model_dump(), user_id=current_user.id)
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.patch("/{campaign_id}/status", response_model=CampaignOut)
async def update_status(
    campaign_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    allowed = {"draft", "active", "paused", "done"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status debe ser uno de: {allowed}")

    result = await db.execute(
        select(Campaign).where(
            Campaign.id == uuid.UUID(campaign_id),
            Campaign.user_id == current_user.id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    campaign.status = status
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/recipients", status_code=201)
async def add_recipient(
    campaign_id: str,
    data: RecipientAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == uuid.UUID(campaign_id),
            Campaign.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    recipient = CampaignRecipient(
        campaign_id=uuid.UUID(campaign_id),
        email=data.email,
        name=data.name,
    )
    db.add(recipient)
    return {"message": "Destinatario agregado"}
