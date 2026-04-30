import asyncio
from app.database import AsyncSessionLocal, init_db
from app.models.account import EmailAccount, WarmupPool, WarmupLog
from app.models.user import User
from app.models.analytics import AnalyticsEvent
from app.models.campaign import Campaign
from sqlalchemy import select

async def seed_pool():
    # Ensure tables exist
    await init_db()
    
    async with AsyncSessionLocal() as db:
        emails = [
            "seed1@nexusengine.com",
            "seed2@nexusengine.com",
            "partner1@alicelabs.co",
            "partner2@alicelabs.co",
            "test_receiver@gmail.com"
        ]
        
        for email in emails:
            # Check if exists
            from sqlalchemy import select
            res = await db.execute(select(WarmupPool).where(WarmupPool.email == email))
            if not res.scalar_one_or_none():
                pool_item = WarmupPool(email=email, name=email.split("@")[0], category="global")
                db.add(pool_item)
        
        await db.commit()
        print(f"[OK] Seeded {len(emails)} emails into WarmupPool")

if __name__ == "__main__":
    asyncio.run(seed_pool())
