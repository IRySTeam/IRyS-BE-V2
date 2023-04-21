from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.document.models import Document, DocumentIndex
from core.db import Transactional, session
from core.exceptions import NotFoundException


class DocumentService:
    """
    DocumentService is a class that handles the business logic for document when
    interacting with the database.
    """

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
        title: str,
        file_url: str,
        elastic_doc_id: int = None,
        elastic_index_name: int = None,
    ) -> Document:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            elastic_doc_id: int = None -> Document id in Elasticsearch.
            elastic_index_name: int = None -> Elasticsearch index name.
        """
        document = Document(
            title=title,
            file_url=file_url,
            elastic_doc_id=elastic_doc_id,
            elastic_index_name=elastic_index_name,
        )
        session.add(document)
        await session.flush()
        document_index = DocumentIndex(doc_id=document.id)
        session.add(document_index)
        document.index = document_index
        return document
