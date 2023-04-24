from sqlalchemy import select

from app.user.models import User
from core.db.session import session
from core.repository import BaseRepo


class UserRepo(BaseRepo[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalars().first()
