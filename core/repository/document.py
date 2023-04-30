from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

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

    async def monitor_all_documents(
        self,
        repository_id: int,
        status: str = "ALL",
        page_size: int = 10,
        page_no: int = 1,
    ) -> dict:
        query = (
            select(Document)
            .where(Document.repository_id == repository_id)
            .options(selectinload(Document.index))
        )
        if status != "ALL":
            query = query.where(Document.index.has(status=status))

        result = await session.execute(query)
        full_items = result.fetchall()
        total_items = len(full_items)
        total_pages = (total_items + page_size - 1) // page_size

        query = query.limit(page_size).offset((page_no - 1) * page_size)
        result = await session.execute(query)
        data = result.scalars().all()

        return {
            "results": data,
            "current_page": page_no,
            "total_pages": total_pages,
            "total_items": total_items,
        }
