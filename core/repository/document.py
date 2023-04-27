from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import text

from app.document.models import Document
from core.db.session import session
from core.repository import BaseRepo


class DocumentRepo(BaseRepo[Document]):
    def __init__(self):
        super().__init__(Document)

    async def get_all(self, include_index: bool = False) -> List[Document]:
        query = select(self.model)
        if include_index:
            query = query.options(selectinload(self.model.index))
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, id: int, include_index: bool = False) -> Document:
        query = select(self.model).where(self.model.id == id)
        if include_index:
            query = query.options(selectinload(self.model.index))
        result = await session.execute(query)
        return result.scalars().first()

    async def find_documents_by_repository_id(self, repository_id: int):
        query = (
            select(Document)
            .where(Document.repository_id == repository_id)
            .options(selectinload(Document.index))
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_role_by_document_id_and_collaborator_id(
        document_id: int, collaborator_id: int
    ) -> Optional[str]:
        query = """
        SELECT ud.role
        FROM user_documents ud
        WHERE ud.user_id = :user_id AND ud.document_id = :document_id
        """
        result = await session.execute(
            text(query), {"user_id": collaborator_id, "document_id": document_id}
        )
        if result.rowcount == 0:
            return None
        return result.fetchone().role
