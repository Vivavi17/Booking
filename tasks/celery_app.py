from celery import Celery
from celery.schedules import crontab

from config import settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["tasks.tasks", "tasks.scheduled"],
)

celery_app.conf.beat_schedule = {
    "print_12345": {"task": "periodic_task", "schedule": 10},
    "notify_1_day": {
        "task": "notification_1_day",
        "schedule": crontab(minute="00", hour="09"),
    },
    "notify_3_days": {
        "task": "notification_3_days",
        "schedule": crontab(minute="30", hour="15"),
    },
}
