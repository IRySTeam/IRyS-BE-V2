from datetime import datetime, timedelta

from app.user.models import User
from app.user.schemas import *
from core.db import Transactional
from core.exceptions import (
    DuplicateEmailException,
    EmailAlreadyVerifiedException,
    EmailNotVerifiedException,
    ExpiredOTPException,
    ForgotPasswordOTPAlreadySentException,
    ForgotPasswordOTPNotVerifiedException,
    InvalidEmailException,
    InvalidPasswordException,
    PasswordDoesNotMatchException,
    TokenAlreadyUsedException,
    UserNotFoundException,
    WrongOTPException,
)
from core.repository import UserRepo
from core.utils.hash_helper import HashHelper
from core.utils.mailer import Mailer
from core.utils.string_helper import StringHelper
from core.utils.token_helper import TokenHelper


class UserService:
    user_repo = UserRepo()

    def __init__(self):
        ...

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
        otp = StringHelper.random_string_number(4)

        # Save to DB
        user = await self.user_repo.save(
            {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password": HashHelper.get_hash(password),
                "otp": otp,
                "otp_valid_until": datetime.utcnow() + timedelta(minutes=5),
            }
        )

        # Send OTP to user's email
        await Mailer.send_registration_otp_email(
            email, {"first_name": first_name, "otp": otp}
        )

        access_token = TokenHelper.encode(
            payload={
                "user_id": user.inserted_primary_key[0],
                "is_email_verified": False,
            }
        )
        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.inserted_primary_key[0],
            params={
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until,
            },
        )

        return RegisterResponseSchema(token=access_token, refresh_token=refresh_token)

    @Transactional()
    async def login(self, email: str, password: str) -> LoginResponseSchema:
        user = await self.user_repo.get_by_email(email=email)

        if not user:
            raise UserNotFoundException

        if not HashHelper.check_hash(password, user.password):
            raise PasswordDoesNotMatchException

        if user.otp is not None:
            raise EmailNotVerifiedException

        access_token = TokenHelper.encode(
            payload={
                "user_id": user.id,
                "is_email_verified": True,
            }
        )
        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "last_login": datetime.utcnow(),
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until,
            },
        )

        response = LoginResponseSchema(
            token=access_token,
            refresh_token=refresh_token,
        )
        return response

    @Transactional()
    async def verify_otp(self, user_id: int, otp: str) -> VerifyOTPResponseSchema:
        user = await self.user_repo.get_by_id(id=user_id)

        if not user:
            raise UserNotFoundException

        if not user.otp:
            raise EmailAlreadyVerifiedException

        if user.otp == otp:
            diff = datetime.utcnow() - user.otp_valid_until
            if diff.total_seconds() > 0:
                raise ExpiredOTPException

            # Update user
            await self.user_repo.update_by_id(
                id=user.id,
                params={"otp": None, "otp_valid_until": None},
            )

            return VerifyOTPResponseSchema(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            )
        else:
            raise WrongOTPException

    @Transactional()
    async def resend_otp(self, user_id: int) -> ResendOTPResponseSchema:
        user = await self.user_repo.get_by_id(id=user_id)

        if not user:
            raise UserNotFoundException

        if not user.otp:
            raise EmailAlreadyVerifiedException

        # Generate OTP
        otp = StringHelper.random_string_number(4)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "otp": otp,
                "otp_valid_until": datetime.utcnow() + timedelta(minutes=5),
            },
        )

        # Send OTP to user's email
        await Mailer.send_registration_otp_email(
            user.email, {"first_name": user.first_name, "otp": otp}
        )

        access_token = TokenHelper.encode(
            payload={
                "user_id": user.id,
                "is_email_verified": False,
            }
        )
        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until,
            },
        )

        return ResendOTPResponseSchema(token=access_token, refresh_token=refresh_token)

    @Transactional()
    async def verify_email(self, email: str) -> VerifyEmailResponseSchema:
        user = await self.user_repo.get_by_email(email=email)

        if not user:
            raise UserNotFoundException

        if not user.otp:
            raise EmailAlreadyVerifiedException

        # Generate OTP
        otp = StringHelper.random_string_number(4)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "otp": otp,
                "otp_valid_until": datetime.utcnow() + timedelta(minutes=5),
            },
        )

        # Send OTP to user's email
        await Mailer.send_registration_otp_email(
            user.email, {"first_name": user.first_name, "otp": otp}
        )

        access_token = TokenHelper.encode(
            payload={
                "user_id": user.id,
                "is_email_verified": False,
            }
        )
        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until,
            },
        )

        return VerifyEmailResponseSchema(
            token=access_token, refresh_token=refresh_token
        )

    @Transactional()
    async def send_forgot_password_otp(
        self, email: str
    ) -> SendForgotPasswordOTPResponseSchema:
        user = await self.user_repo.get_by_email(email=email)

        if not user:
            raise UserNotFoundException

        if user.otp is not None:
            raise EmailNotVerifiedException

        if (
            user.forgot_password_otp is not None
            or user.forgot_password_otp_valid_until is not None
        ):
            diff = datetime.utcnow() - user.forgot_password_otp_valid_until
            if diff.total_seconds() <= 0:
                raise ForgotPasswordOTPAlreadySentException

        # Generate OTP
        otp = StringHelper.random_string_number(4)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "forgot_password_otp": otp,
                "forgot_password_otp_valid_until": datetime.utcnow()
                + timedelta(minutes=5),
            },
        )

        # Send OTP to user's email
        await Mailer.send_forgot_password_otp_email(
            user.email, {"first_name": user.first_name, "otp": otp}
        )

        access_token = TokenHelper.encode(
            payload={
                "user_id": user.id,
                "is_email_verified": True,
                "is_forgot_password_otp_verified": False,
            }
        )
        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until,
            },
        )

        return SendForgotPasswordOTPResponseSchema(
            token=access_token, refresh_token=refresh_token
        )

    @Transactional()
    async def resend_forgot_password_otp(
        self, user_id: int
    ) -> ResendForgotPasswordOTPResponseSchema:
        user = await self.user_repo.get_by_id(id=user_id)

        if not user:
            raise UserNotFoundException

        if user.otp is not None:
            raise EmailNotVerifiedException

        # Generate OTP
        otp = StringHelper.random_string_number(4)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "forgot_password_otp": otp,
                "forgot_password_otp_valid_until": datetime.utcnow()
                + timedelta(minutes=5),
            },
        )

        # Send OTP to user's email
        await Mailer.send_forgot_password_otp_email(
            user.email, {"first_name": user.first_name, "otp": otp}
        )

        access_token = TokenHelper.encode(
            payload={
                "user_id": user.id,
                "is_email_verified": True,
                "is_forgot_password_otp_verified": False,
            }
        )
        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until,
            },
        )

        return ResendForgotPasswordOTPResponseSchema(
            token=access_token, refresh_token=refresh_token
        )

    @Transactional()
    async def verify_forgot_password_otp(
        self, user_id: int, otp: str
    ) -> VerifyForgotPasswordOTPResponseSchema:
        user = await self.user_repo.get_by_id(id=user_id)

        if not user:
            raise UserNotFoundException

        if user.forgot_password_otp == otp:
            diff = datetime.utcnow() - user.forgot_password_otp_valid_until
            if diff.total_seconds() > 0:
                raise ExpiredOTPException

            access_token = TokenHelper.encode(
                payload={
                    "user_id": user.id,
                    "is_email_verified": True,
                    "is_forgot_password_otp_verified": True,
                }
            )
            raw_refresh_token = StringHelper.random_string(10)
            refresh_token = HashHelper.get_hash(raw_refresh_token)
            refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)

            # Update user
            await self.user_repo.update_by_id(
                id=user.id,
                params={
                    "forgot_password_otp": None,
                    "forgot_password_otp_valid_until": None,
                    "refresh_token": raw_refresh_token,
                    "refresh_token_valid_until": refresh_token_valid_until,
                },
            )

            return VerifyForgotPasswordOTPResponseSchema(
                token=access_token, refresh_token=refresh_token
            )
        else:
            raise WrongOTPException

    @Transactional()
    async def change_password(
        self, user_id: int, new_password: str, confirm_new_password: str
    ) -> ChangePasswordResponseSchema:
        user = await self.user_repo.get_by_id(id=user_id)

        if not user:
            raise UserNotFoundException

        if new_password != confirm_new_password or not StringHelper.validate_password(
            new_password
        ):
            raise InvalidPasswordException

        if (
            user.forgot_password_otp is not None
            or user.forgot_password_otp_valid_until is not None
        ):
            raise ForgotPasswordOTPNotVerifiedException

        if user.refresh_token is None or user.refresh_token_valid_until is None:
            raise TokenAlreadyUsedException

        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "password": HashHelper.get_hash(new_password),
                "refresh_token": None,
                "refresh_token_valid_until": None,
            },
        )

        return ChangePasswordResponseSchema(message="Success")

    async def search_user_for_repository_collaborator(
        self, query: str, repository_id: int, page_no: int, page_size: int
    ) -> SearchUserResponseSchema:
        (
            users,
            total_pages,
            total_items,
        ) = await self.user_repo.find_by_name_or_email_and_repository_id(
            query=query,
            repository_id=repository_id,
            page_no=page_no,
            page_size=page_size,
        )
        results = []
        for user in users:
            results.append(
                UserResponseSchema(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                )
            )

        return SearchUserResponseSchema(
            results=results,
            total_pages=total_pages,
            total_items=total_items,
        )
