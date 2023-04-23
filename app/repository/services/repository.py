from typing import List

from core.db import Transactional
from core.exceptions import RepositoryDetailsEmptyException, NotFoundException
from core.repository import RepositoryRepo
from celery_app import parsing, celery
from app.elastic import EsClient
from app.document.models import Document
from app.document.services import document_service
from app.document.enums.document import IndexingStatusEnum
from app.repository.schemas import (
    CreateRepositoryResponseSchema,
    RepositorySchema,
    GetJoinedRepositoriesSchema,
    RepositoryOwnerSchema,
    GetPublicRepositoriesResponseSchema,
)


class RepositoryService:
    repository_repo = RepositoryRepo()

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
            print(repo)
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
        print(does_user_have_any_repos)
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

    async def reindex_all(self, repository_id: int = None):
        # Find the repository
        repository = await self.repository_repo.get_by_id(repository_id, True, True)
        if not repository:
            raise NotFoundException("Repository with specified id not found")
        documents: List[Document] = repository.documents
        for document in documents:
            await document_service.reindex(document)
