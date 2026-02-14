from celery import Celery
from celery.schedules import crontab

import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "trade_finance",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.beat_schedule = {
    "run-integrity-check-every-5-minutes": {
        "task": "app.tasks.integrity_check_job",
        "schedule": crontab(minute="*/5"),  # every 5 minutes
    }
}

# 🔽 ADD THIS
celery_app.autodiscover_tasks(["app"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
