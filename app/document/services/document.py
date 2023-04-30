from typing import List

from asgiref.sync import async_to_sync
from fastapi import UploadFile

from app.document.enums.document import IndexingStatusEnum
from app.document.models import Document, DocumentIndex
from app.document.schemas import DocumentSchema
from app.elastic import EsClient
from app.elastic.configuration import GENERAL_ELASTICSEARCH_INDEX_NAME
from app.repository.enums import RepositoryRole
from core.db import Transactional, standalone_session
from core.exceptions import (
    InvalidRepositoryRoleException,
    NotFoundException,
    RepositoryNotFoundException,
    UserNotAllowedException,
)
from core.repository import DocumentIndexRepo, DocumentRepo, RepositoryRepo
from core.utils import GCStorage


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

    @async_to_sync
    @standalone_session
    async def get_document_by_id_celery(
        self, id: int, include_index: bool = False
    ) -> Document:
        """
        Get a document by id but with a standalone session.
        [Parameters]
            id: int -> Document id.
            include_index: bool = False -> Whether to include the indexing status of the document.
        [Returns]
            Document -> Document.
        """
        data = await self.document_repo.get_by_id(id=id, include_index=include_index)
        print("TESTING")
        print(type(data))
        if not data:
            raise NotFoundException("Document not with specified id not found")
        return data

    @Transactional()
    async def create_document(
        self,
        title: str,
        repository_id: int,
        file_url: str = "dummy",
        general_elastic_doc_id: str = None,
        elastic_doc_id: str = None,
        elastic_index_name: str = None,
        mimetype: str = None,
        extension: str = None,
        size: int = None,
    ) -> int:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            repository_id: int -> Repository id.
            file_url: str = "dummy" -> Document url.
            general_elastic_doc_id: str = None -> General document id in Elasticsearch.
            elastic_doc_id: str = None -> Document id in Elasticsearch.
            elastic_index_name: str = None -> Elasticsearch index name.
            mimetype: str = None -> Document mimetype.
            extension: str = None -> Document extension.
            size: int = None -> Document size.
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
                "file_url": file_url,
                "general_elastic_doc_id": general_elastic_doc_id,
                "elastic_doc_id": elastic_doc_id,
                "elastic_index_name": elastic_index_name,
                "mimetype": mimetype,
                "extension": extension,
                "size": size,
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
        params: dict,
    ) -> Document:
        """
        Update a document.
        [Parameters]
            id: int -> Document id.
            params: dict -> Document parameters.
        [Returns]
            Document -> Document.
        """
        # Construct params
        await self.document_repo.update_by_id(
            id=id,
            params=params,
        )
        return await self.get_document_by_id(id)

    @standalone_session
    @Transactional()
    async def update_document_celery(
        self,
        id: int,
        params: dict,
    ) -> Document:
        """
        Update a document.
        [Parameters]
            id: int -> Document id.
            params: dict -> Document parameters.
        [Returns]
            Document -> Document.
        """
        await self.document_repo.update_by_id(
            id=id,
            params=params,
        )
        return await self.get_document_by_id(id)

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

        index: DocumentIndex = document.index

        # Revoke the task if indexing is still in progress.
        if index.status != IndexingStatusEnum.SUCCESS and index.current_task_id:
            celery.control.revoke(index.current_task_id, terminate=True)
            await self.document_index_repo.update_by_doc_id(
                doc_id=document.id,
                params={
                    "status": IndexingStatusEnum.FAILED,
                    "reason": "Terminated because of re-indexing",
                    "current_task_id": None,
                },
            )

        # Delete corresponding index in elasticsearch if exist, also remove it in db.
        if index.status == IndexingStatusEnum.SUCCESS:
            if document.general_elastic_doc_id:
                # Ignore if document doesn't exists in elasticsearch.
                EsClient.safe_delete_doc(
                    GENERAL_ELASTICSEARCH_INDEX_NAME, document.general_elastic_doc_id
                )
                document.general_elastic_doc_id = None
            if document.elastic_doc_id and document.elastic_index_name:
                # Ignore if document doesn't exists in elasticsearch.
                EsClient.safe_delete_doc(
                    document.elastic_index_name, document.elastic_doc_id
                )
                document.elastic_doc_id = None
                document.elastic_index_name = None

            await self.document_repo.update_by_id(
                id=document.id,
                params={
                    "general_elastic_doc_id": document.general_elastic_doc_id,
                    "elastic_doc_id": document.elastic_doc_id,
                    "elastic_index_name": document.elastic_index_name,
                },
            )

        # Re-index the document.
        parsing.delay(
            document_id=document.id,
            document_title=document.title,
            document_url=document.file_url,
        )

    async def reindex_by_id(self, doc_id: int, user_id: int) -> None:
        """
        Reindex a document.
        [Parameters]
            doc_id: int -> Id of the corresponding document.
            user_id: int -> The user who request the reindexing.
        """
        document = await self.get_document_by_id(doc_id, True)
        repository_id = document.repository_id

        # User permission check.
        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException
        if not (
            await self.repository_repo.is_user_id_owner_of_repository(
                user_id, repository_id
            )
            or await self.repository_repo.is_user_id_admin_of_repository(
                user_id, repository_id
            )
        ):
            raise UserNotAllowedException
        await self.reindex(document)

    async def monitor_all_document(
        self,
        user_id: int,
        repository_id: int,
        status: str = None,
        page_size: int = 10,
        page_no: int = 1,
    ) -> dict:
        """
        Monitor all documents in a repository.
        [Parameters]
            user_id: int -> User that wants to monitor the documents.
            repository_id: int -> Repository id.
            status: str = None -> Indexing status.
            page_size: int = 10 -> Page size.
            page_no: int = 1 -> Page number.
        [Returns]
            List[Document] -> List of documents with indexing status.
        """
        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException
        if not (
            await self.repository_repo.is_user_id_owner_of_repository(
                user_id, repository_id
            )
            or await self.repository_repo.is_user_id_admin_of_repository(
                user_id, repository_id
            )
        ):
            raise UserNotAllowedException

        return await self.document_repo.monitor_all_documents(
            status=status,
            repository_id=repository_id,
            page_no=page_no,
            page_size=page_size,
        )

    async def check_user_access_upload_document(
        self,
        user_id: int,
        repository_id: int,
    ) -> bool:
        """
        Check if user has access to upload document.
        [Parameters]
            user_id: int -> User id.
            repository_id: int -> Repository id.
        """
        user_role = (
            await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                user_id, repository_id
            )
        )
        if not user_role:
            raise UserNotAllowedException

        if user_role.upper() in RepositoryRole.__members__:
            user_role = RepositoryRole[user_role.upper()]

            if user_role < RepositoryRole.UPLOADER:
                raise UserNotAllowedException
        else:
            raise InvalidRepositoryRoleException

    @Transactional()
    async def process_upload_document(
        self,
        repository_id: int,
        file: UploadFile,
    ) -> Document:
        """
        Upload document and create task to index it.
        [Parameters]
            repository_id: int -> Id of the corresponding repository.
            file: UploadFile -> File to be uploaded.
        """
        from celery_app import parsing

        document: Document = None

        try:
            title = ".".join(file.filename.split(".")[:-1])

            # Upload file to GCS
            uploaded_file_url = GCStorage().upload_file(file, "documents/")

            doc_id = await DocumentService().create_document(
                title=title,
                repository_id=repository_id,
                file_url=uploaded_file_url,
            )
            document = await DocumentService().get_document_by_id(
                id=doc_id, include_index=True
            )

            parsing.delay(
                document_id=document.id,
                document_title=title,
                document_url=uploaded_file_url,
            )

            return document

        except Exception as e:
            # Delete the document if there is an error.
            if document:
                await self.delete_document(document.id)
            raise e

    @Transactional()
    async def upload_document(
        self,
        user_id: int,
        repository_id: int,
        file: UploadFile,
    ) -> Document:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            elastic_doc_id: int = None -> Document id in Elasticsearch.
            elastic_index_name: int = None -> Elasticsearch index name.
        """
        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException

        await self.check_user_access_upload_document(
            user_id=user_id,
            repository_id=repository_id,
        )

        return await self.process_upload_document(repository_id, file)

    @Transactional()
    async def upload_multiple_document(
        self,
        user_id: int,
        repository_id: int,
        files: List[UploadFile],
    ) -> List[Document]:
        """
        Create a document and the corresponding indexing status.
        [Parameters]
            title: str -> Document title.
            elastic_doc_id: int = None -> Document id in Elasticsearch.
            elastic_index_name: int = None -> Elasticsearch index name.
        """
        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException

        await self.check_user_access_upload_document(
            user_id=user_id,
            repository_id=repository_id,
        )

        files_response = []
        for file in files:
            processed_file = await self.process_upload_document(repository_id, file)
            files_response.append(processed_file)

        return files_response

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
