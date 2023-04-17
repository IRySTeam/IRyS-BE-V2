from app.repository.schemas import CreateRepositoryResponseSchema
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
