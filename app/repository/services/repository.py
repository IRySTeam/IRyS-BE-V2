from typing import List

from app.repository.schemas import (
    CreateRepositoryResponseSchema,
    RepositorySchema,
    GetJoinedRepositoriesSchema,
    RepositoryOwnerSchema,
    GetPublicRepositoriesResponseSchema,
)
from core.db import Transactional
from core.exceptions import RepositoryDetailsEmptyException
from core.repository import RepositoryRepo


class RepositoryService:
    repository_repo = RepositoryRepo()

    def __init__(self):
        ...

    @Transactional()
    async def create_repository(
        self, user_id: int, name: str, description: str, is_public: bool
    ) -> CreateRepositoryResponseSchema:
        if not name or not description or is_public is None:
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
                    owner=RepositoryOwnerSchema(
                        id=repo.owner_id,
                        first_name=repo.owner_first_name,
                        last_name=repo.owner_last_name,
                    ),
                )
            )
        return GetJoinedRepositoriesSchema(
            results=results, total_page=total_page, total_items=total_items
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
