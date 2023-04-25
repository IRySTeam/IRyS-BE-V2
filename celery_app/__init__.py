from celery_app.main import celery
from celery_app.tasks import extraction, indexing, parsing

__all__ = ["celery", "parsing", "extraction", "indexing"]
