from typing import List

from asgiref.sync import async_to_sync
from fastapi import UploadFile

from app.document.enums import DocumentRole, IndexingStatusEnum
from app.document.models import Document, DocumentIndex
from app.document.schemas import DocumentCollaboratorSchema, DocumentSchema
from app.elastic import EsClient
from app.elastic.configuration import GENERAL_ELASTICSEARCH_INDEX_NAME
from app.repository.enums import RepositoryRole
from core.db import Transactional, standalone_session
from core.exceptions import (
    DocumentCollaboratorAlreadyExistException,
    DocumentCollaboratorNotFoundException,
    DocumentNotFoundException,
    InvalidDocumentRoleException,
    InvalidRepositoryRoleException,
    NotFoundException,
    RepositoryNotFoundException,
    UserNotAllowedException,
    UserNotFoundException,
)
from core.repository import (
    DocumentIndexRepo,
    DocumentRepo,
    RepositoryRepo,
    UserRepo,
)
from core.utils import GCStorage


class DocumentService:
    """
    DocumentService is a class that handles the business logic for document when
    interacting with the database.
    """

    repository_repo = RepositoryRepo()
    document_repo = DocumentRepo()
    document_index_repo = DocumentIndexRepo()
    user_repo = UserRepo()

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
            raise NotFoundException("Document with specified id not found")
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
            raise NotFoundException("Document with specified ids not found")
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
        find_document: str = None,
    ) -> dict:
        """
        Monitor all documents in a repository.
        [Parameters]
            user_id: int -> User that wants to monitor the documents.
            repository_id: int -> Repository id.
            status: str = None -> Indexing status.
            page_size: int = 10 -> Page size.
            page_no: int = 1 -> Page number.
            find_document: str = None -> Find document by title.
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

    async def edit_document(
        self, user_id: int, repo_id: int, document_id: int, params: dict
    ):
        if not self.document_repo.is_exist(document_id):
            raise DocumentNotFoundException

        repo_role = (
            await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                user_id=user_id, repository_id=repo_id
            )
        )

        if not repo_role:
            raise UserNotAllowedException
        if repo_role.upper() in RepositoryRole.__members__:
            repo_role = RepositoryRole[repo_role.upper()]

            if repo_role < RepositoryRole.ADMIN:
                doc_role = await self.document_repo.get_role_by_document_id_and_collaborator_id(
                    collaborator_id=user_id, document_id=document_id
                )
                if not doc_role:
                    raise UserNotAllowedException

                if doc_role.upper() in DocumentRole.__members__:
                    doc_role = DocumentRole[doc_role.upper()]
                    if doc_role < DocumentRole.EDITOR:
                        raise UserNotAllowedException
                else:
                    raise InvalidDocumentRoleException
        else:
            raise InvalidRepositoryRoleException

        params = {k: v for k, v in params.items() if v is not None}
        await self.document_repo.update_by_id(document_id, params)

    async def get_document_collaborators(
        self, user_id: int, repository_id: int, document_id: int
    ) -> List[DocumentCollaboratorSchema]:
        document = await self.document_repo.get_by_id(document_id)

        if not document:
            raise DocumentNotFoundException

        if not document.is_public:
            repo_role = (
                await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                    user_id=user_id, repository_id=repository_id
                )
            )

            if not repo_role:
                raise UserNotAllowedException
            if repo_role.upper() in RepositoryRole.__members__:
                repo_role = RepositoryRole[repo_role.upper()]

                if repo_role < RepositoryRole.ADMIN:
                    doc_role = await self.document_repo.get_role_by_document_id_and_collaborator_id(
                        collaborator_id=user_id, document_id=document_id
                    )
                    if not doc_role:
                        raise UserNotAllowedException

                    if not doc_role.upper() in DocumentRole.__members__:
                        raise InvalidDocumentRoleException

            else:
                raise InvalidRepositoryRoleException

        collaborators = await self.document_repo.get_collaborators_by_document_id(
            document_id=document_id, repository_id=repository_id
        )

        results = []
        for collaborator in collaborators:
            results.append(
                DocumentCollaboratorSchema(
                    id=collaborator.id,
                    first_name=collaborator.first_name,
                    last_name=collaborator.last_name,
                    email=collaborator.email,
                    role=collaborator.role,
                )
            )
        return collaborators

    async def add_document_collaborator(
        self,
        user_id: int,
        repository_id: int,
        document_id: int,
        collaborator_id: int,
        role: str,
    ) -> None:
        document = await self.document_repo.get_by_id(document_id)

        if not await self.user_repo.is_exist(collaborator_id):
            raise UserNotFoundException

        if not document:
            raise DocumentNotFoundException

        repo_role = (
            await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                user_id=user_id, repository_id=repository_id
            )
        )

        if not repo_role:
            raise UserNotAllowedException
        if repo_role.upper() in RepositoryRole.__members__:
            repo_role = RepositoryRole[repo_role.upper()]

            if repo_role < RepositoryRole.ADMIN:
                doc_role = await self.document_repo.get_role_by_document_id_and_collaborator_id(
                    collaborator_id=user_id, document_id=document_id
                )
                if not doc_role:
                    raise UserNotAllowedException

                if doc_role.upper() in DocumentRole.__members__:
                    doc_role = DocumentRole[doc_role.upper()]

                    if doc_role < DocumentRole.EDITOR:
                        raise UserNotAllowedException

                    if role.upper() in DocumentRole.__members__:
                        role = DocumentRole[role.upper()]
                        if role > doc_role or role == doc_role:
                            raise UserNotAllowedException

                        await self.document_repo.add_collaborator(
                            document_id, collaborator_id, role.name
                        )
                    else:
                        raise InvalidDocumentRoleException
                else:
                    raise InvalidDocumentRoleException
        else:
            raise InvalidRepositoryRoleException

        if await self.document_repo.is_collaborator_exist(document_id, collaborator_id):
            raise DocumentCollaboratorAlreadyExistException

        if not role.upper() in DocumentRole.__members__:
            raise InvalidDocumentRoleException

        role = DocumentRole[role.upper()]

        if role is DocumentRole.OWNER:
            raise UserNotAllowedException

        await self.document_repo.add_collaborator(
            document_id, collaborator_id, role.name.title()
        )

    async def edit_document_collaborator(
        self,
        user_id: int,
        repository_id: int,
        document_id: int,
        collaborator_id: int,
        role: str,
    ) -> None:
        document = await self.document_repo.get_by_id(document_id)

        if not self.user_repo.is_exist(collaborator_id):
            raise UserNotFoundException

        if not document:
            raise DocumentNotFoundException

        repo_role = (
            await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                user_id=user_id, repository_id=repository_id
            )
        )

        if not repo_role:
            raise UserNotAllowedException
        if repo_role.upper() in RepositoryRole.__members__:
            repo_role = RepositoryRole[repo_role.upper()]

            if repo_role < RepositoryRole.ADMIN:
                doc_role = await self.document_repo.get_role_by_document_id_and_collaborator_id(
                    collaborator_id=user_id, document_id=document_id
                )
                if not doc_role:
                    raise UserNotAllowedException

                if doc_role.upper() in DocumentRole.__members__:
                    doc_role = DocumentRole[doc_role.upper()]

                    if doc_role < DocumentRole.EDITOR:
                        raise UserNotAllowedException

                    if role.upper() in DocumentRole.__members__:
                        role = DocumentRole[role.upper()]
                        if role > DocumentRole.VIEWER:
                            raise UserNotAllowedException

                        await self.document_repo.edit_collaborator(
                            document_id, collaborator_id, role.name
                        )
                    else:
                        raise InvalidDocumentRoleException
                else:
                    raise InvalidDocumentRoleException
        else:
            raise InvalidRepositoryRoleException

        if not await self.document_repo.is_collaborator_exist(
            document_id, collaborator_id
        ):
            raise DocumentCollaboratorNotFoundException

        if not role.upper() in DocumentRole.__members__:
            raise InvalidDocumentRoleException

        role = DocumentRole[role.upper()]

        if role is DocumentRole.OWNER:
            raise UserNotAllowedException

        await self.document_repo.edit_collaborator(
            document_id, collaborator_id, role.name.title()
        )

    async def delete_document_collaborator(
        self, user_id: int, repository_id: int, document_id: int, collaborator_id: int
    ) -> None:
        document = await self.document_repo.get_by_id(document_id)

        if not self.user_repo.is_exist(collaborator_id):
            raise UserNotFoundException

        if not document:
            raise DocumentNotFoundException

        repo_role = (
            await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                user_id=user_id, repository_id=repository_id
            )
        )

        if not repo_role:
            raise UserNotAllowedException
        if repo_role.upper() in RepositoryRole.__members__:
            repo_role = RepositoryRole[repo_role.upper()]

            if repo_role < RepositoryRole.ADMIN:
                doc_role = await self.document_repo.get_role_by_document_id_and_collaborator_id(
                    collaborator_id=user_id, document_id=document_id
                )
                if not doc_role:
                    raise UserNotAllowedException

                if doc_role.upper() in DocumentRole.__members__:
                    doc_role = DocumentRole[doc_role.upper()]

                    if doc_role < DocumentRole.EDITOR:
                        raise UserNotAllowedException

                    await self.document_repo.delete_collaborator(
                        document_id, collaborator_id
                    )
                else:
                    raise InvalidDocumentRoleException
        else:
            raise InvalidRepositoryRoleException

        if not self.document_repo.is_collaborator_exist(document_id, collaborator_id):
            raise DocumentCollaboratorNotFoundException

        await self.document_repo.delete_collaborator(document_id, collaborator_id)

    async def get_all_accessible_documents(self, user_id: int) -> List[int]:
        """
        Get all document ids that a user has access to, either in their repositories or public documents.
        [Parameters]
            user_id: int -> User id.
        [Returns]
            List[int] -> List[int].
        """
        data = await self.document_repo.get_all_accessible_documents(
            collaborator_id=user_id
        )
        if not data:
            raise NotFoundException("No accessible documents found")
        return data

    async def get_repo_accessible_documents(self, repository_id: int) -> List[int]:
        """
        Get all document ids within a specific repository.
        [Parameters]
            user_id: int -> User id.
        [Returns]
            List[int] -> List[int].
        """
        data = await self.document_repo.get_repo_accessible_documents(
            repository_id=repository_id
        )
        if not data:
            raise NotFoundException("No accessible documents found")
        return data
