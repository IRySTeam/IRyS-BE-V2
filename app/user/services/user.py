from typing import Optional, List

from sqlalchemy import or_, select, and_, update, insert
from datetime import datetime, timedelta

from app.user.models import User
from app.user.schemas.user import LoginResponseSchema, RegisterResponseSchema, VerifyOTPResponseSchema
from core.db import Transactional, session
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailException,
    UserNotFoundException,
    ExpiredOTPException,
    WrongOTPException,
    InvalidEmailException,
    InvalidPasswordException,
    EmailAlreadyVerifiedException
)
from core.repository import UserRepo
from core.utils.token_helper import TokenHelper
from core.utils.hash_helper import HashHelper
from core.utils.string_helper import StringHelper
from core.utils.mailer import Mailer


class UserService:
    user_repo = UserRepo()

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
        return await self.user_repo.get_by_id(id=id)

    @Transactional()
    async def register_user(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> RegisterResponseSchema:
        # Check if email is already exist
        is_exist = await self.user_repo.get_by_email(email=email)
        if is_exist:
            raise DuplicateEmailException
        
        if not StringHelper.validate_email(email):
            raise InvalidEmailException
        
        if not StringHelper.validate_password(password):
            raise InvalidPasswordException

        # Generate OTP
        otp = StringHelper.random_string_number(6)
        
        # Save to DB
        user = await self.user_repo.save({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": HashHelper.get_hash(password),
            "otp": otp,
            "otp_valid_until": datetime.utcnow() + timedelta(minutes=5)
        })

        # Send OTP to user's email
        await Mailer.send_registration_otp_email(email, { "first_name": first_name, "otp": otp })
        
        access_token = TokenHelper.encode(payload={"user_id": user.inserted_primary_key[0], "is_email_verified": False,})
        refresh_token = HashHelper.get_hash(StringHelper.random_string(10))
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.inserted_primary_key[0],
            params={
                "refresh_token": refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until
            },
        )

        return RegisterResponseSchema(token=access_token, refresh_token=refresh_token)
        

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

        access_token = TokenHelper.encode(payload={"user_id": user.id, "is_email_verified": True,})
        refresh_token = HashHelper.get_hash(StringHelper.random_string(10))
        refresh_token_valid_until = TokenHelper.get_refresh_token_valid_until(7)
        
        # Update user
        user.last_login = datetime.utcnow()
        user.refresh_token = refresh_token
        user.refresh_token_valid_until = refresh_token_valid_until

        await session.commit()
        
        response = LoginResponseSchema(
            token=access_token,
            refresh_token=refresh_token,
        )
        return response
    
    async def verify_otp(self, user_id: int, otp: str) -> VerifyOTPResponseSchema: 
        user = await self.user_repo.get_by_id(id=user_id)

        if not user:
            raise UserNotFoundException
        
        if not user.otp:
            raise EmailAlreadyVerifiedException
        
        if (user.otp == otp):
            diff = datetime.utcnow() - user.otp_valid_until
            diff_in_seconds = diff.total_seconds()

            if (diff_in_seconds > 300):
                raise ExpiredOTPException

            # Update user
            await self.user_repo.update_by_id(
                id=user.id,
                params={
                    "otp": None,
                    "otp_valid_until": None
                },
            )
            
            return VerifyOTPResponseSchema(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            )
        else:
            raise WrongOTPException
