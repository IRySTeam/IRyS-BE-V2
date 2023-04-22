from binascii import b2a_base64
from typing import List
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.document.models import Document
from app.document.schemas import (
    DocumentResponseSchema,
    DocumentIndexing,
    DocumentSchema,
)
from app.document.enums.document import IndexingStatusEnum
from app.repository.enums import RepositoryRole
from celery_app import parsing
from core.db import Transactional, session
from core.exceptions import (
    NotFoundException,
    UserNotAllowedException,
    InvalidRepositoryRoleException,
    RepositoryNotFoundException,
)
from core.repository import DocumentRepo, DocumentIndexRepo, RepositoryRepo
from core.utils import GCStorage


class DocumentService:
    """
    DocumentService is a class that handles the business logic for document when
    interacting with the database.
    """

    document_repo = DocumentRepo()
    document_index_repo = DocumentIndexRepo()
    repository_repo = RepositoryRepo()

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

        file.file.seek(0)
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

        documents = await self.document_repo.get_documents_by_repository_id(
            repository_id, include_index=True
        )
        return documents

    @Transactional()
    async def upload_document(
        self,
        user_id: int,
        repository_id: int,
        file: UploadFile,
    ) -> DocumentResponseSchema:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            elastic_doc_id: int = None -> Document id in Elasticsearch.
            elastic_index_name: int = None -> Elasticsearch index name.
        """
        user_role = (
            await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                user_id, repository_id
            )
        )

        if not user_role:
            raise UserNotAllowedException

        if user_role.upper() in RepositoryRepo:
            user_role = RepositoryRepo[user_role.upper()]

            if user_role < RepositoryRole.UPLOADER:
                raise UserNotAllowedException
        else:
            raise InvalidRepositoryRoleException

        # TODO: Is this the correct way to get the title?
        title = ".".join(file.filename.split(".")[:-1])

        # Upload file to GCS
        uploaded_file_url = GCStorage().upload_file(file, "documents/")
        document = await self.document_repo.save(
            {
                "title": title,
                "file_url": uploaded_file_url,
                "repository_id": repository_id,
            }
        )
        document_index = await self.document_index_repo.save(
            {
                "doc_id": document.inserted_primary_key[0],
            }
        )

        # TODO: Add with OCR choice.
        # TODO: Add check duplicate.

        file.file.seek(0)
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
