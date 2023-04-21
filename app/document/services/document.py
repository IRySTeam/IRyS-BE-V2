from binascii import b2a_base64
from typing import List
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.document.models import Document, DocumentIndex
from app.document.schemas import DocumentResponseSchema, DocumentIndexing
from app.document.enums.document import IndexingStatusEnum
from celery_app import parsing
from core.db import Transactional, session
from core.exceptions import NotFoundException
from core.repository import DocumentRepo, DocumentIndexRepo
from core.utils import GCStorage


class DocumentService:
    """
    DocumentService is a class that handles the business logic for document when
    interacting with the database.
    """

    document_repo = DocumentRepo()
    document_index_repo = DocumentIndexRepo()

    def __init__(self):
        ...

    async def get_document_list(
        self,
        include_index: bool = False,
    ) -> List[Document]:
        """
        Get all documents.
        [Parameters]
            include_index: bool = False -> Whether to include the indexing status of the document.
        [Returns]
            List[Document] -> List of documents.
        """
        query = select(Document)
        include_index = False
        if include_index:
            query = query.options(selectinload(Document.index))
        result = await session.execute(query)
        data = result.scalars().all()
        # Return the dict representation of the object to avoid pydantic accessing doc.index
        # to lazy load the indexing status.
        return [doc.__dict__ for doc in data]

    async def get_document_by_id(
        self, id: int, include_index: bool = False
    ) -> Document:
        """
        Get a document by id.
        [Parameters]
            id: int -> Document id.
            include_index: bool = False -> Whether to include the indexing status of the document.
        [Returns]
            Document -> Document.
        """
        query = select(Document).where(Document.id == id)
        if include_index:
            query = query.options(selectinload(Document.index))
        result = await session.execute(query)
        data = result.scalars().first()
        if not data:
            raise NotFoundException("Document not with specified id not found")
        # Return the dict representation of the object to avoid pydantic accessing doc.index
        # to lazy load the indexing status.
        return data.__dict__

    @Transactional()
    async def create_document(
        self,
        file: UploadFile,
    ) -> DocumentResponseSchema:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            elastic_doc_id: int = None -> Document id in Elasticsearch.
            elastic_index_name: int = None -> Elasticsearch index name.
        """
        # TODO: Is this the correct way to get the title?
        title = ".".join(file.filename.split(".")[:-1])

        # Upload file to GCS
        uploaded_file_url = GCStorage().upload_file(file, "documents/")
        document = await self.document_repo.save(
            {
                "title": title,
                "file_url": uploaded_file_url,
            }
        )
        document_index = await self.document_index_repo.save(
            {
                "doc_id": document.inserted_primary_key[0],
            }
        )

        # TODO: Add with OCR choice.
        # TODO: Add check duplicate.

        print(b2a_base64(file.file.read()).decode("utf-8"))
        parsing.delay(
            document_id=document.inserted_primary_key[0],
            document_title=title,
            file_content_str=b2a_base64(file.file.read()).decode("utf-8"),
        )
        return DocumentResponseSchema(
            id=document.inserted_primary_key[0],
            title=title,
            file_url=uploaded_file_url,
            index=DocumentIndexing(
                id=document_index.inserted_primary_key[0],
                doc_id=document.inserted_primary_key[0],
                status=IndexingStatusEnum.READY,
            ),
        )
