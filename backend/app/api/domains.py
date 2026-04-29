import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.analytics import Domain
from app.schemas.analytics import DomainCreate, DomainResponse, DNSCheckResult
from app.core.security import get_current_user
from app.services.dns_checker import check_dns

router = APIRouter(prefix="/api/v1/domains", tags=["Domains"])


@router.post("/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def add_domain(
    data: DomainCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain).where(Domain.domain_name == data.domain_name, Domain.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dominio ya registrado")

    domain = Domain(
        user_id=current_user.id,
        domain_name=data.domain_name,
    )
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    return DomainResponse.model_validate(domain)


@router.get("/", response_model=List[DomainResponse])
async def list_domains(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain).where(Domain.user_id == current_user.id)
    )
    domains = result.scalars().all()
    return [DomainResponse.model_validate(d) for d in domains]


@router.get("/{domain_id}/dns-check", response_model=DNSCheckResult)
async def run_dns_check(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id, Domain.user_id == current_user.id)
    )
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Dominio no encontrado")

    try:
        dns_result = await asyncio.wait_for(check_dns(domain.domain_name), timeout=10.0)
    except asyncio.TimeoutError:
        dns_result = {
            "spf": {"status":"timeout","record":None,"details":"DNS timeout"},
            "dkim": {"status":"timeout","record":None,"details":"DNS timeout"},
            "dmarc": {"status":"timeout","record":None,"details":"DNS timeout"},
        }
    except Exception as e:
        dns_result = {
            "spf": {"status":"error","record":None,"details":str(e)},
            "dkim": {"status":"error","record":None,"details":str(e)},
            "dmarc": {"status":"error","record":None,"details":str(e)},
        }

    # Update domain with DNS results
    domain.spf_status = dns_result["spf"]["status"]
    domain.dkim_status = dns_result["dkim"]["status"]
    domain.dmarc_status = dns_result["dmarc"]["status"]
    domain.overall_ok = all(
        dns_result[r]["status"] == "ok" for r in ("spf", "dkim", "dmarc")
    )
    domain.spf_record = dns_result["spf"].get("record")
    domain.dkim_record = dns_result["dkim"].get("record")
    domain.dmarc_record = dns_result["dmarc"].get("record")

    import datetime
    domain.last_checked_at = datetime.datetime.now(datetime.timezone.utc)

    await db.commit()

    return DNSCheckResult(
        domain=domain.domain_name,
        spf=dns_result["spf"],
        dkim=dns_result["dkim"],
        dmarc=dns_result["dmarc"],
        overall_ok=domain.overall_ok,
    )


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id, Domain.user_id == current_user.id)
    )
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Dominio no encontrado")
    await db.delete(domain)
    await db.commit()
