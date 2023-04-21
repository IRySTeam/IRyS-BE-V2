from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.document.models import Document, DocumentIndex
from core.db import Transactional, session, standalone_session
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
        if include_index:
            query = query.options(selectinload(Document.index))
        result = await session.execute(query)
        data = result.scalars().all()
        return data

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
        return data

    @Transactional()
    async def create_document(
        self,
        title: str,
        doc_created_at: datetime = None,
        doc_updated_at: datetime = None,
        elastic_doc_id: str = None,
        elastic_index_name: str = None,
    ) -> Document:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        """
        document = Document(
            title=title,
            doc_created_at=doc_created_at,
            doc_updated_at=doc_updated_at,
            elastic_doc_id=elastic_doc_id,
            elastic_index_name=elastic_index_name,
        )
        session.add(document)
        await session.flush()
        document_index = DocumentIndex(doc_id=document.id)
        session.add(document_index)
        document.index = document_index
        return document

    @Transactional()
    async def update_document(
        self,
        id: int,
        title: str,
        doc_created_at: datetime = None,
        doc_updated_at: datetime = None,
        elastic_doc_id: int = None,
        elastic_index_name: str = None,
    ) -> Document:
        """
        Update a document.
        [Parameters]
            id: int -> Document id.
            title: str -> Document title.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        [Returns]
            Document -> Document.
        """
        document = await self.get_document_by_id(id)
        document.title = title
        document.doc_created_at = doc_created_at
        document.doc_updated_at = doc_updated_at
        document.elastic_doc_id = elastic_doc_id
        document.elastic_index_name = elastic_index_name
        return document

    @Transactional()
    async def partial_update_document(
        self,
        id: int,
        title: str = None,
        doc_created_at: datetime = None,
        doc_updated_at: datetime = None,
        elastic_doc_id: int = None,
        elastic_index_name: str = None,
    ) -> Document:
        """
        Partially update a document.
        [Parameters]
            id: int -> Document id.
            title: str -> Document title.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        [Returns]
            Document -> Document.
        """
        document = await self.get_document_by_id(id)
        if title:
            document.title = title
        if doc_created_at:
            document.doc_created_at = doc_created_at
        if doc_updated_at:
            document.doc_updated_at = doc_updated_at
        if elastic_doc_id:
            document.elastic_doc_id = elastic_doc_id
        if elastic_index_name:
            document.elastic_index_name = elastic_index_name
        return document

    @standalone_session
    @Transactional()
    async def partial_update_document_celery(
        self,
        id: int,
        title: str = None,
        doc_created_at: datetime = None,
        doc_updated_at: datetime = None,
        elastic_doc_id: str = None,
        elastic_index_name: str = None,
    ) -> Document:
        """
        Partially update a document but with a standalone session.
        [Parameters]
            id: int -> Document id.
            title: str -> Document title.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        [Returns]
            Document -> Document.
        """
        document = await self.get_document_by_id(id)
        if title:
            document.title = title
        if doc_created_at:
            document.doc_created_at = doc_created_at
        if doc_updated_at:
            document.doc_updated_at = doc_updated_at
        if elastic_doc_id:
            document.elastic_doc_id = elastic_doc_id
        if elastic_index_name:
            document.elastic_index_name = elastic_index_name
        return document

    @Transactional()
    async def delete_document(self, id: int) -> bool:
        """
        Delete a document and the corresponding indexing status.
        [Parameters]
            id: int -> Document id.
        [Returns]
            bool -> True if successful.
        """
        document = await self.get_document_by_id(id)
        await session.delete(document)
        await session.delete(document.index)
        return True
