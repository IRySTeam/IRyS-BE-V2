from sqlalchemy import update

from core.db import  session, Transactional
from app.document.enums.document import IndexingStatusEnum
from app.document.models import DocumentIndex

class DocumentIndexService:
    """
    DocumentIndexService is a class that handles the business logic for document index when
    interacting with the database.
    """
    
    def __init__(self):
        ...
    
    @Transactional()
    async def update_indexing_status(
        self,
        doc_id: int,
        status: IndexingStatusEnum,
        reason: str = None,
    ) -> None:
        """
        Update the indexing status of a document.
        [Parameters]
            doc_id: int -> Document id.
            status: IndexingStatusEnum -> Indexing status.
            reason: str -> Reason for the indexing status.
        """
        update_stmt = (
            update(DocumentIndex)
            .where(DocumentIndex.doc_id == doc_id)
            .values(
                status=status,
                reason=reason,
            )
        )
        session.execute(update_stmt)