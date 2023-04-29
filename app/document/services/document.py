from datetime import datetime
from typing import List

from app.document.enums.document import IndexingStatusEnum
from app.document.models import Document
from app.document.schemas import DocumentSchema
from app.elastic import EsClient
from core.db import Transactional, standalone_session
from core.exceptions import (
    InvalidRepositoryRoleException,
    NotFoundException,
    RepositoryNotFoundException,
    UserNotAllowedException,
)
from core.repository import DocumentIndexRepo, DocumentRepo, RepositoryRepo


class DocumentService:
    """
    DocumentService is a class that handles the business logic for document when
    interacting with the database.
    """

    repository_repo = RepositoryRepo()
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
        return await self.document_repo.get_all(include_index=include_index)

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
        data = await self.document_repo.get_by_id(id=id, include_index=include_index)
        if not data:
            raise NotFoundException("Document not with specified id not found")
        return data
    
    async def get_document_by_ids(
        self, ids: List[int], include_index: bool = False
    ) -> Document:
        """
        Get a document by id.
        [Parameters]
            id: int -> Document id.
            include_index: bool = False -> Whether to include the indexing status of the document.
        [Returns]
            Document -> Document.
        """
        data = await self.document_repo.get_by_ids(ids=ids, include_index=include_index)
        if not data:
            raise NotFoundException("Document not with specified id not found")
        return data

    @Transactional()
    async def create_document(
        self,
        title: str,
        repository_id: int,
        file_content_str: str,
        doc_created_at: datetime = None,
        doc_updated_at: datetime = None,
        elastic_doc_id: str = None,
        elastic_index_name: str = None,
    ) -> int:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            repository_id: int -> Repository id.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        [Returns]
            int -> Document id.
        """
        repository = await self.repository_repo.get_by_id(id=repository_id)
        if not repository:
            raise NotFoundException("Repository with specified id not found")
        document = await self.document_repo.save(
            {
                "title": title,
                "repository_id": repository_id,
                "file_content_str": file_content_str,
                "doc_created_at": doc_created_at,
                "doc_updated_at": doc_updated_at,
                "elastic_doc_id": elastic_doc_id,
                "elastic_index_name": elastic_index_name,
            }
        )

        await self.document_index_repo.save(
            {"doc_id": document.inserted_primary_key[0]}
        )
        return document.inserted_primary_key[0]

    @Transactional()
    async def update_document(
        self,
        id: int,
        title: str = None,
        repository_id: int = None,
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
            repository_id: int -> Repository id.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        [Returns]
            Document -> Document.
        """
        document = await self.get_document_by_id(id)
        await self.document_repo.update_by_id(
            id=id,
            params={
                "title": title or document.title,
                "repository_id": repository_id or document.repository_id,
                "doc_created_at": doc_created_at or document.doc_created_at,
                "doc_updated_at": doc_updated_at or document.doc_updated_at,
                "elastic_doc_id": elastic_doc_id or document.elastic_doc_id,
                "elastic_index_name": elastic_index_name or document.elastic_index_name,
            },
        )
        document = await self.get_document_by_id(id)
        return document

    @standalone_session
    @Transactional()
    async def update_document_celery(
        self,
        id: int,
        title: str = None,
        repository_id: int = None,
        doc_created_at: datetime = None,
        doc_updated_at: datetime = None,
        elastic_doc_id: int = None,
        elastic_index_name: str = None,
    ) -> bool:
        """
        Update a document.
        [Parameters]
            id: int -> Document id.
            title: str -> Document title.
            repository_id: int -> Repository id.
            doc_created_at: datetime -> Document created at.
            doc_updated_at: datetime -> Document updated at.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
        [Returns]
            bool -> True if successful.
        """
        document = await self.get_document_by_id(id)
        await self.document_repo.update_by_id(
            id=id,
            params={
                "title": title or document.title,
                "repository_id": repository_id or document.repository_id,
                "doc_created_at": doc_created_at or document.doc_created_at,
                "doc_updated_at": doc_updated_at or document.doc_updated_at,
                "elastic_doc_id": elastic_doc_id or document.elastic_doc_id,
                "elastic_index_name": elastic_index_name or document.elastic_index_name,
            },
        )
        return True

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
        await self.document_index_repo.delete(document.index)
        await self.document_repo.delete_by_id(document.index.id)
        return True

    @Transactional()
    async def reindex(self, document: Document):
        """
        Logic for reindexing a document.
        [Parameters]
            document: Document -> Document to be reindexed.
        """
        # Fuck partial dependency.
        from celery_app import celery, parsing

        index = document.index

        # Revoke the task if indexing is still in progress.
        if index.status != IndexingStatusEnum.SUCCESS and not (index.current_task_id):
            celery.control.revoke(index.current_task_id, terminate=True)

        # Delete corresponding index in elasticsearch if exist, also remove it in db.
        if (
            index.status == IndexingStatusEnum.SUCCESS
            and document.elastic_doc_id
            and document.elastic_index_name
        ):
            EsClient.delete_doc(document.elastic_index_name, document.elastic_doc_id)
            await self.update_document(
                id=document.id,
                elastic_doc_id=None,
                elastic_index_name=None,
            )
        parsing.delay(
            document_id=document.id,
            document_title=document.title,
            file_content_str=document.file_content_str,
        )

    async def reindex_by_id(self, id: int) -> None:
        """
        Reindex a document.
        [Parameters]
            id: int -> Document id.
        """
        document = await self.get_document_by_id(id, True)
        await self.reindex(document)

    async def get_repository_documents(
        self,
        user_id: int,
        repository_id: int,
    ) -> List[DocumentSchema]:
        """
        Get all documents in a repository.
        [Parameters]
            repository_id: int -> Repository id.
        [Returns]
            List[Document] -> List of documents.
        """
        repo = await self.repository_repo.get_repository_by_id(repository_id)

        if not repo:
            raise RepositoryNotFoundException

        if not repo.is_public:
            user_role = (
                await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                    user_id, repository_id
                )
            )
            if not user_role:
                raise UserNotAllowedException

            if not user_role.upper() in RepositoryRepo:
                raise InvalidRepositoryRoleException

        documents = await self.document_repo.find_documents_by_repository_id(
            repository_id
        )
        return documents
