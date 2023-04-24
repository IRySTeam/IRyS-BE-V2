from typing import List, Tuple
from sqlalchemy import select, or_
from sqlalchemy.sql import func

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

    async def find_by_name_or_email(
        self, query: str, page_no: int, page_size: int
    ) -> Tuple[List[User], int, int]:
        query = (
            select(User)
            .where(
                or_(
                    User.email.ilike(f"%{query}%"),
                    func.concat(User.first_name, User.last_name).ilike(f"%{query}%"),
                )
            )
            .offset((page_no - 1) * page_size)
            .limit(page_size)
        )
        result = await session.execute(query)

        # Get total pages and total items
        query = select(func.count(User.id)).where(
            or_(
                User.email.ilike(f"%{query}%"),
                func.concat(User.first_name, " ", User.last_name).ilike(f"%{query}%"),
            )
        )
        result2 = await session.execute(query)
        total_items = result2.scalars().first()
        total_pages = (total_items + page_size - 1) // page_size

        return result.scalars().all(), total_pages, total_items
