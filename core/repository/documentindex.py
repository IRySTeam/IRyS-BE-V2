from sqlalchemy import select, update

from app.document.models import DocumentIndex
from core.db.session import session
from core.repository import BaseRepo
from core.repository.enum import SynchronizeSessionEnum


class DocumentIndexRepo(BaseRepo[DocumentIndex]):
    def __init__(self):
        super().__init__(DocumentIndex)

    async def get_by_doc_id(self, doc_id: int) -> DocumentIndex:
        query = select(self.model).where(self.model.doc_id == doc_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def update_by_doc_id(
        self,
        doc_id: int,
        params: dict,
        synchronize_session: SynchronizeSessionEnum = False,
    ):
        query = (
            update(self.model)
            .where(self.model.doc_id == doc_id)
            .values(**params)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)
