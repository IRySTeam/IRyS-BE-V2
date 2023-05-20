from celery import Celery
from app.search.services.text_encoding_manager import TextEncodingManager

from core.config import config

celery = Celery(
    "worker",
    backend=config.CELERY_BACKEND_URL,
    broker=config.CELERY_BROKER_URL,
    include=["celery_app.tasks"],
)
celery.conf.update(task_track_started=True)
celery.conf.timezone = "Asia/Jakarta"
