from core.repository import BaseRepo
from app.document.models import Document


class DocumentRepo(BaseRepo[Document]):
    def __init__(self):
        super().__init__(Document)
