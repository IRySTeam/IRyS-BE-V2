from celery_app.main import celery
from celery_app.tasks import parsing, extraction, indexing

__all__ = ["celery", "parsing", "extraction", "indexing"]
