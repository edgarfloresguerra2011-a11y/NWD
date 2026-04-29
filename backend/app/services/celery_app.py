from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "nwd",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.services.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Ejecutar warmup cada hora en horas laborales
        "warmup-emails-hourly": {
            "task": "app.services.tasks.run_warmup_batch",
            "schedule": crontab(minute=0, hour="8-18"),
        },
        # Resetear contador diario a medianoche
        "reset-daily-counters": {
            "task": "app.services.tasks.reset_daily_counters",
            "schedule": crontab(minute=0, hour=0),
        },
    },
)
