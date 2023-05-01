from typing import List

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.document.models import Document
from app.user.models import user_documents
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

    async def delete_by_repository_id(self, repository_id: int):
        query = delete(Document).where(Document.repository_id == repository_id)
        await session.execute(query)

    async def delete_user_documents_by_repository_id(
        self, repository_id: int, user_id: int
    ):
        query = (
            delete(user_documents)
            .where(user_documents.c.user_id == user_id)
            .where(
                user_documents.c.document_id.in_(
                    session.query(Document.id).filter(
                        Document.repository_id == repository_id
                    )
                )
            )
        )
        await session.execute(query)
