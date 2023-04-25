from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.sql import text

from core.repository import BaseRepo
from app.user.models import User
from core.db.session import session


class UserRepo(BaseRepo[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalars().first()

    async def find_by_name_or_email_and_repository_id(
        self, query: str, repository_id: int, page_no: int, page_size: int
    ) -> Tuple[List[User], int, int]:
        sql = """
            SELECT DISTINCT u.*
            FROM users u
            LEFT JOIN user_repositories ur ON ur.user_id = u.id
            WHERE (CONCAT(u.first_name, ' ', u.last_name) ILIKE :query OR u.email ILIKE :query)
            AND (ur.repository_id IS NULL OR ur.repository_id != :repository_id)
            LIMIT :limit OFFSET :offset
            """
        result = await session.execute(
            text(sql),
            {
                "query": f"%{query}%",
                "repository_id": repository_id,
                "limit": page_size,
                "offset": (page_no - 1) * page_size,
            },
        )

        # Get total pages and total items
        sql = """
            SELECT COUNT(DISTINCT u.*)
            FROM users u
            LEFT JOIN user_repositories ur ON ur.user_id = u.id
            WHERE (CONCAT(u.first_name, ' ', u.last_name) ILIKE :query OR u.email ILIKE :query)
            AND (ur.repository_id IS NULL OR ur.repository_id != :repository_id)
            """
        result2 = await session.execute(
            text(sql), {"query": f"%{query}%", "repository_id": repository_id}
        )
        total_items = result2.scalars().first()
        total_pages = (total_items + page_size - 1) // page_size

        return result.fetchall(), total_pages, total_items
