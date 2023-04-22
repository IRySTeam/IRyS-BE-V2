from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.repository import BaseRepo
from app.document.models import Document
from core.db.session import session


class DocumentRepo(BaseRepo[Document]):
    def __init__(self):
        super().__init__(Document)

    async def get_documents_by_repository_id(
        self, repository_id: int, include_index: bool = False
    ):
        query = select(Document).where(Document.repository_id == repository_id)
        if include_index:
            query = query.options(selectinload(Document.index))
        result = await session.execute(query)
        return result.scalars().all()
