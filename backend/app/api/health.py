"""
Nexus Warmup Engine — Deep Health Check
Goes beyond "status: ok" — reports real system health.
"""
from fastapi import APIRouter
from app.core.observability import metrics
from app.database import engine
from app.config import settings
from sqlalchemy import text
import time
import logging

logger = logging.getLogger("nexus.health")
router = APIRouter(prefix="/api/v1/health", tags=["Health & Observability"])


@router.get("")
async def basic_health():
    """Quick health check for load balancers and uptime monitors."""
    return {"status": "ok", "version": settings.VERSION, "app": settings.APP_NAME}


@router.get("/deep")
async def deep_health():
    """
    Production-grade health check that reports:
    - Database connectivity + query latency
    - Metrics snapshot (throughput, latency percentiles, error rates)
    - System component status
    """
    checks = {}
    overall_healthy = True
    
    # 1. Database check
    try:
        start = time.perf_counter()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_latency = round((time.perf_counter() - start) * 1000, 2)
        checks["database"] = {
            "status": "healthy",
            "latency_ms": db_latency,
        }
        if db_latency > 500:
            checks["database"]["warning"] = "Slow query detected"
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False
    
    # 2. Redis check (for Celery)
    try:
        import redis as redis_lib
        r = redis_lib.from_url(settings.REDIS_URL, socket_timeout=2)
        start = time.perf_counter()
        r.ping()
        redis_latency = round((time.perf_counter() - start) * 1000, 2)
        checks["redis"] = {"status": "healthy", "latency_ms": redis_latency}
    except Exception as e:
        checks["redis"] = {"status": "unavailable", "note": "Celery tasks will not execute"}
        # Not marking as unhealthy — app can run without Redis in dev mode
    
    # 3. AI service check
    if settings.OPENROUTER_API_KEY:
        checks["ai_service"] = {"status": "configured", "model": settings.AI_MODEL}
    else:
        checks["ai_service"] = {"status": "not_configured", "fallback": "static_templates"}
    
    # 4. Stripe check
    if settings.STRIPE_API_KEY:
        checks["payments"] = {"status": "configured"}
    else:
        checks["payments"] = {"status": "not_configured"}
    
    # 5. Metrics snapshot
    snap = metrics.snapshot()
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "version": settings.VERSION,
        "checks": checks,
        "metrics": snap,
    }


@router.get("/metrics")
async def get_metrics():
    """Raw metrics endpoint for monitoring dashboards (Datadog, Grafana, etc.)."""
    return metrics.snapshot()
