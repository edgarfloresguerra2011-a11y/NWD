from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignStep
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/campaigns", tags=["Campaigns"])


def _campaign_to_response(campaign: Campaign) -> CampaignResponse:
    resp = CampaignResponse.model_validate(campaign)
    resp.open_rate = campaign.open_rate if hasattr(campaign, "open_rate") else 0.0
    resp.reply_rate = campaign.reply_rate if hasattr(campaign, "reply_rate") else 0.0
    return resp


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = Campaign(
        user_id=current_user.id,
        name=data.name,
        status="draft",
    )
    db.add(campaign)
    await db.flush()

    for step_data in data.steps:
        step = CampaignStep(
            campaign_id=campaign.id,
            step_order=step_data.step_order,
            action=step_data.action,
            subject=step_data.subject,
            body_text=step_data.body_text,
            delay_hours=step_data.delay_hours,
            condition_field=step_data.condition_field,
            condition_value=step_data.condition_value,
        )
        db.add(step)

    await db.commit()
    # Refresh with selectinload to avoid MissingGreenlet
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign.id)
    )
    campaign = result.scalar_one()
    return _campaign_to_response(campaign)


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.user_id == current_user.id)
        .order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    return [_campaign_to_response(c) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    return _campaign_to_response(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    if data.name is not None:
        campaign.name = data.name
    if data.status is not None:
        campaign.status = data.status

    if data.steps is not None:
        for old_step in campaign.steps:
            await db.delete(old_step)
        for step_data in data.steps:
            step = CampaignStep(
                campaign_id=campaign.id,
                step_order=step_data.step_order,
                action=step_data.action,
                subject=step_data.subject,
                body_text=step_data.body_text,
                delay_hours=step_data.delay_hours,
            )
            db.add(step)

    await db.commit()
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one()
    return _campaign_to_response(campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    await db.delete(campaign)
    await db.commit()


@router.post("/{campaign_id}/launch", response_model=CampaignResponse)
async def launch_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Solo se pueden lanzar campañas en borrador")

    campaign.status = "running"
    await db.commit()
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one()
    return _campaign_to_response(campaign)


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    campaign.status = "paused"
    await db.commit()
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.steps))
        .where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one()
    return _campaign_to_response(campaign)
