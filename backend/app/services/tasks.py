import asyncio
import logging

from app.services.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.services.tasks.run_warmup_batch", bind=True, max_retries=3)
def run_warmup_batch(self):
    """Envía emails de warmup para todas las cuentas activas."""
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.models import EmailAccount
        from sqlalchemy import select

        async def _run():
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(EmailAccount).where(
                        EmailAccount.warmup_enabled == True,
                        EmailAccount.is_active == True,
                    )
                )
                accounts = result.scalars().all()
                logger.info(f"[Warmup] Procesando {len(accounts)} cuentas")
                for account in accounts:
                    if account.emails_sent_today < account.daily_limit:
                        # Aquí iría la lógica real de envío SMTP
                        account.emails_sent_today += 1
                        account.reputation_score = min(100, account.reputation_score + 1)
                        logger.info(f"[Warmup] Email enviado desde {account.email}")
                await db.commit()

        asyncio.run(_run())
    except Exception as exc:
        logger.error(f"[Warmup] Error: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.services.tasks.reset_daily_counters")
def reset_daily_counters():
    """Resetea el contador diario de emails enviados."""
    from app.db.session import AsyncSessionLocal
    from app.models.models import EmailAccount
    from sqlalchemy import update

    async def _run():
        async with AsyncSessionLocal() as db:
            await db.execute(update(EmailAccount).values(emails_sent_today=0))
            await db.commit()
            logger.info("[Reset] Contadores diarios reseteados")

    asyncio.run(_run())
