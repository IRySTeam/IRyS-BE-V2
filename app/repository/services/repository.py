from typing import List

from app.document.enums.document import IndexingStatusEnum
from app.document.models import Document
from app.document.services import document_service
from app.repository.constants import GRANTABLE_ROLES
from app.repository.schemas import (
    CreateRepositoryResponseSchema,
    GetJoinedRepositoriesSchema,
    GetPublicRepositoriesResponseSchema,
    RepositoryCollaboratorSchema,
    RepositoryDetailsResponseSchema,
    RepositoryOwnerSchema,
    RepositorySchema,
)
from core.db import Transactional
from core.exceptions import (
    DuplicateCollaboratorException,
    InvalidRepositoryCollaboratorException,
    InvalidRepositoryRoleException,
    NotFoundException,
    RepositoryDetailsEmptyException,
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
from core.utils.mailer import Mailer


class RepositoryService:
    repository_repo = RepositoryRepo()
    document_index_repo = DocumentIndexRepo()
    document_repo = DocumentRepo()

    def __init__(self):
        ...

    @Transactional()
    async def create_repository(
        self, user_id: int, name: str, description: str, is_public: bool
    ) -> CreateRepositoryResponseSchema:
        if not name or description is None or is_public is None:
            raise RepositoryDetailsEmptyException
        repo = await self.repository_repo.save(
            user_id=user_id,
            params={"name": name, "description": description, "is_public": is_public},
            role="Owner",
        )

        return CreateRepositoryResponseSchema(
            name=name, description=description, is_public=is_public
        )

    async def get_joined_repositories(
        self,
        user_id: int,
        name: str,
        type: str,
        sort_by: str,
        page_no: int,
        page_size: int,
    ) -> GetJoinedRepositoriesSchema:
        (
            repositories,
            total_page,
            total_items,
        ) = await self.repository_repo.get_joined_repositories(
            user_id=user_id,
            name=name,
            type=type,
            order_by=sort_by,
            page_no=page_no,
            page_size=page_size,
        )
        results = []
        for repo in repositories:
            results.append(
                RepositorySchema(
                    id=repo.id,
                    name=repo.name,
                    description=repo.description,
                    is_public=repo.is_public,
                    updated_at=repo.updated_at,
                    owner=RepositoryOwnerSchema(
                        id=repo.owner_id,
                        first_name=repo.owner_first_name,
                        last_name=repo.owner_last_name,
                    ),
                )
            )
        does_user_have_any_repos = (
            await self.repository_repo.does_user_id_have_any_repository(user_id=user_id)
        )
        return GetJoinedRepositoriesSchema(
            does_user_have_any_repos=does_user_have_any_repos,
            results=results,
            total_page=total_page,
            total_items=total_items,
        )

    async def get_public_repositories(
        self, name: str, page_no: int, page_size: int
    ) -> GetPublicRepositoriesResponseSchema:
        (
            repositories,
            total_page,
            total_items,
        ) = await self.repository_repo.get_public_repositories(
            name=name, page_no=page_no, page_size=page_size
        )
        results = []
        for repo in repositories:
            results.append(
                RepositorySchema(
                    id=repo.id,
                    name=repo.name,
                    description=repo.description,
                    is_public=repo.is_public,
                    updated_at=repo.updated_at,
                    owner=RepositoryOwnerSchema(
                        id=repo.owner_id,
                        first_name=repo.owner_first_name,
                        last_name=repo.owner_last_name,
                    ),
                )
            )
        return GetPublicRepositoriesResponseSchema(
            results=results, total_page=total_page, total_items=total_items
        )

    async def reindex_all(self, user_id: int, repository_id: int):
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

        # Find the repository and reindex all documents.
        repository = await self.repository_repo.get_by_id(repository_id, True, True)
        if not repository:
            raise NotFoundException("Repository with specified id not found")
        documents: List[Document] = repository.documents
        # Filter for all documents that indexing status is not completed.
        documents = [
            document
            for document in documents
            if document.index.status != IndexingStatusEnum.SUCCESS.value
        ]

        for document in documents:
            await document_service.reindex(document)

    async def get_repository_collaborators(
        self, user_id: int, repository_id: int
    ) -> List[RepositoryCollaboratorSchema]:
        repo = await self.repository_repo.get_repository_by_id(repository_id)
        if not repo.is_public:
            if not await self.repository_repo.is_user_id_collaborator_of_repository(
                user_id=user_id, repository_id=repository_id
            ):
                raise UserNotAllowedException

        members = await self.repository_repo.get_repository_collaborators(
            repository_id=repository_id
        )
        return members

    @Transactional()
    async def edit_repository(
        self, user_id: int, repository_id: int, params: dict
    ) -> None:
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

        params = {k: v for k, v in params.items() if v is not None}
        await self.repository_repo.update_by_id(repository_id, params)

    async def get_repository_details(
        self, user_id: int, repository_id: int
    ) -> RepositorySchema:
        repository = await self.repository_repo.get_repository_by_id(repository_id)
        if not repository:
            raise RepositoryNotFoundException

        current_user_role = "Viewer"
        if not repository.is_public:
            if not await self.repository_repo.is_user_id_collaborator_of_repository(
                user_id, repository_id
            ):
                raise RepositoryNotFoundException
            current_user_role = (
                await self.repository_repo.get_user_role_by_user_id_and_repository_id(
                    user_id, repository_id
                )
            )

        return RepositoryDetailsResponseSchema(
            id=repository.id,
            name=repository.name,
            description=repository.description,
            is_public=repository.is_public,
            updated_at=repository.updated_at,
            current_user_role=current_user_role,
            owner=RepositoryOwnerSchema(
                id=repository.owner_id,
                first_name=repository.owner_first_name,
                last_name=repository.owner_last_name,
            ),
        )

    @Transactional()
    async def add_repository_collaborator(
        self, user_id: int, repository_id: int, params: dict
    ) -> None:
        user_repo = UserRepo()

        if not await user_repo.is_exist(params["collaborator_id"]):
            raise UserNotFoundException

        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException

        if await self.repository_repo.is_user_id_collaborator_of_repository(
            params["collaborator_id"], repository_id
        ):
            raise DuplicateCollaboratorException

        if params["role"] == "Owner":
            raise UserNotAllowedException
        if params["role"] not in GRANTABLE_ROLES:
            raise InvalidRepositoryRoleException

        is_owner = await self.repository_repo.is_user_id_owner_of_repository(
            user_id, repository_id
        )
        is_admin = await self.repository_repo.is_user_id_admin_of_repository(
            user_id, repository_id
        )

        if not (is_owner or is_admin):
            raise UserNotAllowedException
        if is_admin:
            if params["role"] == "Admin":
                raise UserNotAllowedException

        await self.repository_repo.create_user_repository(
            repository_id=repository_id,
            user_id=params["collaborator_id"],
            role=params["role"],
        )

        user_repo = UserRepo()
        user = await user_repo.get_by_id(params["collaborator_id"])
        repo = await self.repository_repo.get_by_id(repository_id)

        # Send email to user
        await Mailer.send_repository_collaborator_email(
            user.email,
            {
                "first_name": user.first_name,
                "repository_name": repo.name,
                "role": params["role"],
            },
        )

    @Transactional()
    async def remove_repository_collaborator(
        self, user_id: int, repository_id: int, collaborator_id: int
    ) -> None:
        user_repo = UserRepo()

        if not await user_repo.is_exist(collaborator_id):
            raise UserNotFoundException

        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException

        is_owner = await self.repository_repo.is_user_id_owner_of_repository(
            user_id, repository_id
        )
        is_admin = await self.repository_repo.is_user_id_admin_of_repository(
            user_id, repository_id
        )
        collaborator = await self.repository_repo.get_collaborator_by_id(
            collaborator_id, repository_id
        )

        if not (is_owner or is_admin):
            raise UserNotAllowedException
        if is_admin:
            if collaborator.role == "Admin":
                raise UserNotAllowedException

        if not await self.repository_repo.is_user_id_collaborator_of_repository(
            collaborator_id, repository_id
        ):
            raise InvalidRepositoryCollaboratorException

        await self.repository_repo.delete_user_repository(
            repository_id=repository_id, user_id=collaborator_id
        )

    @Transactional()
    async def edit_repository_collaborator(
        self, user_id: int, repository_id: int, collaborator_id: int, role: str
    ) -> None:
        user_repo = UserRepo()

        if not await user_repo.is_exist(collaborator_id):
            raise UserNotFoundException
        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException

        if role not in GRANTABLE_ROLES:
            raise InvalidRepositoryRoleException

        is_owner = await self.repository_repo.is_user_id_owner_of_repository(
            user_id, repository_id
        )
        is_admin = await self.repository_repo.is_user_id_admin_of_repository(
            user_id, repository_id
        )
        collaborator = await self.repository_repo.get_collaborator_by_id(
            collaborator_id, repository_id
        )

        if not (is_owner or is_admin):
            raise UserNotAllowedException
        if is_admin:
            if collaborator.role == "Admin":
                raise UserNotAllowedException
            if role == "Admin":
                raise UserNotAllowedException

        if not await self.repository_repo.is_user_id_collaborator_of_repository(
            collaborator_id, repository_id
        ):
            raise InvalidRepositoryCollaboratorException

        await self.repository_repo.update_user_repository_role(
            repository_id=repository_id, user_id=collaborator_id, role=role
        )

    @Transactional()
    async def delete_repository(self, user_id: int, repository_id: int) -> None:
        if not await self.repository_repo.is_exist(repository_id):
            raise RepositoryNotFoundException

        is_owner = await self.repository_repo.is_user_id_owner_of_repository(
            user_id, repository_id
        )
        print("is_owner:", is_owner)
        if not is_owner:
            raise UserNotAllowedException

        # Delete all document_indexes
        await self.document_index_repo.delete_by_repository_id(repository_id)
        print("deleted document_indexes")

        # Delete all user_documents
        await self.document_repo.delete_user_documents_by_repository_id(repository_id)
        print("deleted user_documents")

        # Delete all documents
        await self.document_repo.delete_by_repository_id(repository_id)
        print("deleted documents")

        # Delete all collaborators
        await self.repository_repo.delete_user_repositories_by_repository_id(
            repository_id
        )
        print("deleted collaborators")

        # Delete repository
        await self.repository_repo.delete_by_id(repository_id)
        print("deleted repository")
