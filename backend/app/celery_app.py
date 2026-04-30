from celery import Celery
from app.config import settings

celery_app = Celery(
    "nexus_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "run-warmup-every-hour": {
            "task": "app.tasks.run_warmup_all_accounts",
            "schedule": 3600.0, # Every hour
        },
        "check-replies-every-30-mins": {
            "task": "app.tasks.check_all_replies",
            "schedule": 1800.0,
        },
        "daily-maintenance": {
            "task": "app.tasks.daily_warmup_maintenance",
            "schedule": 86400.0, # Every 24 hours
        },
    },
)

# Auto-discover tasks from app.tasks
celery_app.autodiscover_tasks(["app"])
