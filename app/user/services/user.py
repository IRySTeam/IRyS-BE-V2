from typing import Optional, List

from sqlalchemy import or_, select, and_, update
from datetime import datetime

from app.user.models import User
from app.user.schemas.user import LoginResponseSchema
from core.db import Transactional, session
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrNicknameException,
    UserNotFoundException,
)
from core.utils.token_helper import TokenHelper
from core.utils.hash_helper import HashHelper
from core.utils.string_helper import StringHelper


class UserService:
    def __init__(self):
        ...

    async def get_user_list(
        self,
        limit: int = 12,
        prev: Optional[int] = None,
    ) -> List[User]:
        query = select(User)

        if prev:
            query = query.where(User.id < prev)

        if limit > 12:
            limit = 12

        query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_user_by_id(self, id: int) -> User:
        query = select(User).where(User.id == id)

        result = await session.execute(query)
        return result.scalars().first()

    @Transactional()
    async def create_user(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> None:
        query = select(User).where(or_(User.email == email))
        result = await session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateEmailOrNicknameException

        user = User(email=email, first_name=first_name, last_name=last_name, password=HashHelper.get_hash(password))
        session.add(user)

    async def is_admin(self, user_id: int) -> bool:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_admin is False:
            return False

        return True

    @Transactional()
    async def login(self, email: str, password: str) -> LoginResponseSchema:
        result = await session.execute(
            select(User).where(and_(User.email == email, password == password))
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        if not HashHelper.check_hash(password, user.password):
            raise PasswordDoesNotMatchException

        access_token = TokenHelper.encode(payload={"user_id": user.id})
        refresh_token = HashHelper.get_hash(StringHelper.random_string(10))
        refresh_token_valid_until = TokenHelper.get_refresh_token_valid_until(7)
        
        # Execute query
        await session.execute(update(User)
                              .where(User.id == user.id)
                              .values({ "last_login": datetime.utcnow(),
                                        "refresh_token": refresh_token, 
                                        "refresh_token_valid_until": refresh_token_valid_until 
                                    }))
        
        response = LoginResponseSchema(
            token=access_token,
            refresh_token=refresh_token,
        )
        return response
