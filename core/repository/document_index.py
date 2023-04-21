from core.repository import BaseRepo
from app.document.models import DocumentIndex


class DocumentIndexRepo(BaseRepo[DocumentIndex]):
    def __init__(self):
        super().__init__(DocumentIndex)
