from sqlalchemy import select, and_

from core.repository import BaseRepo
from app.repository.models import Repository
from core.db.session import session
from app.user.models import user_repositories


class RepositoryRepo(BaseRepo[Repository]):
    def __init__(self):
        super().__init__(Repository)

    async def save(self, user_id: int, params: dict, role: str) -> None:
        new_repo = Repository(**params)
        session.add(new_repo)
        await session.flush()

        # Add the new Repository to the User's repositories with the role using session.execute()
        stmt = user_repositories.insert().values(user_id=user_id, repository_id=new_repo.id, role=role)
        await session.execute(stmt)

        return new_repo