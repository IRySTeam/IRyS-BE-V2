from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.repository import BaseRepo
from app.document.models import Document
from core.db.session import session


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
