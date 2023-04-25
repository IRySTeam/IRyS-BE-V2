from app.document.enums.document import IndexingStatusEnum
from app.document.models import DocumentIndex
from core.db import Transactional, standalone_session
from core.exceptions import NotFoundException
from core.repository import DocumentIndexRepo


class DocumentIndexService:
    """
    DocumentIndexService is a class that handles the business logic for document index when
    interacting with the database.
    """

    document_index_repo = DocumentIndexRepo()

    def __init__(self):
        ...

    async def get_by_doc_id(self, doc_id: int) -> DocumentIndex:
        """
        Get indexing status of a document identified by doc_id.
        [Parameters]
            doc_id: int -> Document id.
        [Returns]
            DocumentIndex -> DocumentIndex.
        """
        data = await self.document_index_repo.get_by_doc_id(doc_id)
        if not data:
            raise NotFoundException("Document index with specified doc_id not found")
        return data

    @Transactional()
    async def update_indexing_status(
        self,
        doc_id: int,
        status: IndexingStatusEnum,
        reason: str = None,
        current_task_id: str = None,
    ) -> None:
        """
        Update the indexing status of a document.
        [Parameters]
            doc_id: int -> Document id.
            status: IndexingStatusEnum -> Indexing status.
            reason: str -> Reason for the indexing status.
            current_task_id: str -> Celery task id.
        """
        await self.get_by_doc_id(doc_id)
        await self.document_index_repo.update_by_doc_id(
            doc_id=doc_id,
            params={
                "status": status,
                "reason": reason,
                "current_task_id": current_task_id,
            },
        )

    @standalone_session
    @Transactional()
    async def update_indexing_status_celery(
        self,
        doc_id: int,
        status: IndexingStatusEnum,
        reason: str = None,
        current_task_id: str = None,
    ) -> None:
        """
        Update the indexing status of a document.
        [Parameters]
            doc_id: int -> Document id.
            status: IndexingStatusEnum -> Indexing status.
            reason: str -> Reason for the indexing status.
            current_task_id: str -> Celery task id.
        """
        await self.get_by_doc_id(doc_id)
        await self.document_index_repo.update_by_doc_id(
            doc_id=doc_id,
            params={
                "status": status,
                "reason": reason,
                "current_task_id": current_task_id,
            },
        )
