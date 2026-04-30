import asyncio
import random
import logging
from celery import shared_task
from sqlalchemy import select
from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.account import EmailAccount, WarmupPool, WarmupLog
from app.services.email_service import send_email_smtp
from app.services.ai_service import generate_warmup_content
from app.core.security import decrypt_string
from datetime import datetime, timezone
from app.services.warmup_engine import calculate_daily_target, should_pause_warmup

WARMUP_TEMPLATES = [
    {
        "subject": "Quick question about your services",
        "body": "Hi, I was looking at your website and had a quick question about the pricing for your basic plan. Could you let me know? Thanks!"
    },
    {
        "subject": "Follow up regarding our meeting",
        "body": "Hello, just following up on our discussion from last week. Let me know if you have any updates on the proposal. Best regards."
    },
    {
        "subject": "Introduction: Potential collaboration",
        "body": "Hi there, I've been following your work and would love to discuss a potential collaboration between our teams. Are you free for a quick chat next week?"
    },
    {
        "subject": "Feedback on the recent update",
        "body": "Hey, just wanted to send over some feedback on the new features you released. They look great! Happy to jump on a call to discuss further."
    }
]

@celery_app.task(
    name="app.tasks.run_warmup_for_account",
    bind=True,
    max_retries=3,
    rate_limit="30/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def run_warmup_for_account(self, account_id: int):
    """
    Celery task to execute a warmup cycle for a specific account.
    This runs in a sync context, so we use asyncio.run to call async services.
    Includes rate limits (30/m globally for this task type) and exponential backoff.
    """
    try:
        return asyncio.run(_run_warmup_logic(account_id))
    except Exception as exc:
        logging.error(f"Warmup task failed for account {account_id}: {exc}")
        raise self.retry(exc=exc)


async def _run_warmup_logic(account_id: int):
    async with AsyncSessionLocal() as db:
        # 1. Get account
        result = await db.execute(select(EmailAccount).where(EmailAccount.id == account_id))
        account = result.scalar_one_or_none()
        if not account or account.status == "paused":
            return {"status": "skipped", "reason": "Account not found or paused"}

        # 2. Get random target from pool
        pool_result = await db.execute(select(WarmupPool).where(WarmupPool.is_active == True))
        pool = pool_result.scalars().all()
        if not pool:
            return {"status": "error", "reason": "Warmup pool is empty"}
        
        target = random.choice(pool)

        # 3. Calculate target for today
        daily_max = calculate_daily_target(account.warmup_day, account.warmup_max_per_day, account.warmup_ramp_days)
        if account.emails_sent_today >= daily_max:
            return {"status": "finished", "reason": f"Daily target reached: {daily_max}"}

        # 4. Decrypt password
        password = decrypt_string(account.smtp_password)

        # 5. Generate content (AI or Template)
        ai_content = await generate_warmup_content(account.email.split("@")[0])
        if ai_content:
            subject = ai_content["subject"]
            body = ai_content["body"]
        else:
            # Fallback to static templates
            template = random.choice(WARMUP_TEMPLATES)
            subject = template["subject"]
            body = template["body"]

        # 5. Send email
        success = await send_email_smtp(
            host=account.smtp_host,
            port=account.smtp_port,
            username=account.smtp_username,
            password=password,
            from_email=account.email,
            to_email=target.email,
            subject=subject,
            body=body
        )

        # 6. Log result
        log = WarmupLog(
            account_id=account.id,
            to_email=target.email,
            subject=subject,
            action="sent",
            status="success" if success else "failed",
            created_at=datetime.now(timezone.utc)
        )
        db.add(log)

        if success:
            account.emails_sent_today += 1
            account.last_warmup_at = datetime.now(timezone.utc)
        
        await db.commit()

        return {
            "status": "success" if success else "failed",
            "account": account.email,
            "target": target.email
        }

@celery_app.task(
    name="app.tasks.check_account_replies",
    bind=True,
    max_retries=3,
    rate_limit="60/m",
    autoretry_for=(Exception,),
    retry_backoff=True
)
def check_account_replies(self, account_id: int):
    try:
        return asyncio.run(_check_replies_logic(account_id))
    except Exception as exc:
        logging.error(f"Check replies task failed for account {account_id}: {exc}")
        raise self.retry(exc=exc)


async def _check_replies_logic(account_id: int):
    from app.services.email_service import check_inbox_imap
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EmailAccount).where(EmailAccount.id == account_id))
        account = result.scalar_one_or_none()
        if not account or not account.imap_host:
            return {"status": "skipped"}

        password = decrypt_string(account.smtp_password)
        messages = await check_inbox_imap(
            host=account.imap_host,
            port=account.imap_port,
            username=account.email,
            password=password
        )

        if messages:
            account.replies_today += len(messages)
            # Log as received
            for msg in messages:
                log = WarmupLog(
                    account_id=account.id,
                    to_email=account.email,
                    subject=msg.get("subject"),
                    action="received",
                    status="success",
                    message_id=msg.get("message_id")
                )
                db.add(log)
            await db.commit()
            return {"status": "success", "replies_found": len(messages)}
        
        return {"status": "no_new_replies"}

@celery_app.task(name="app.tasks.daily_warmup_maintenance")
def daily_warmup_maintenance():
    return asyncio.run(_maintenance_logic())

async def _maintenance_logic():
    from app.services.warmup_engine import calculate_reputation_score
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EmailAccount).where(EmailAccount.status != "paused"))
        accounts = result.scalars().all()
        
        for account in accounts:
            # Update reputation
            account.reputation_score = calculate_reputation_score(
                sent=account.emails_sent_today,
                opened=account.opens_today,
                replied=account.replies_today,
                bounced=0, # TODO: integrate bounce detection
                spammed=0  # TODO: integrate spam detection
            )
            
            # Increment day and reset daily stats
            account.warmup_day += 1
            account.emails_sent_today = 0
            account.emails_received_today = 0
            account.opens_today = 0
            account.replies_today = 0
            
        await db.commit()
        return {"status": "maintenance_complete", "accounts_updated": len(accounts)}

@celery_app.task(name="app.tasks.run_warmup_all_accounts")
def run_warmup_all_accounts():
    return asyncio.run(_run_warmup_all_logic())

async def _run_warmup_all_logic():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EmailAccount).where(EmailAccount.status == "warming"))
        accounts = result.scalars().all()
        for account in accounts:
            run_warmup_for_account.delay(account.id)
    return {"status": "batch_queued", "count": len(accounts)}

@celery_app.task(name="app.tasks.check_all_replies")
def check_all_replies():
    return asyncio.run(_check_all_replies_logic())

async def _check_all_replies_logic():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EmailAccount).where(EmailAccount.status == "warming"))
        accounts = result.scalars().all()
        for account in accounts:
            check_account_replies.delay(account.id)
    return {"status": "batch_queued", "count": len(accounts)}
