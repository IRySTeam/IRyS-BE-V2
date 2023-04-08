from typing import List

from fastapi import APIRouter, Depends, Query, Request
from app.user.schemas import *
from app.user.services import UserService
from core.exceptions import (
    InvalidEmailException,
    InvalidPasswordException,
    DuplicateEmailException,
    UserNotFoundException,
    PasswordDoesNotMatchException,
    EmailNotVerifiedException,
    EmailAlreadyVerifiedException,
    ExpiredOTPException,
    WrongOTPException,
    UnauthorizedException,
    ForgotPasswordOTPNotVerifiedException,
    TokenAlreadyUsedException,
    ForgotPasswordOTPAlreadySentException
)
from core.utils import (
    CustomExceptionHelper
)
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
    IsEmailNotVerified,
    IsEmailVerified,
    IsForgotPasswordOtpNotVerified,
    IsForgotPasswordOtpVerified
)

user_router = APIRouter()

@user_router.get(
    "/me",
    response_model=GetUserByIdResponseSchema,
    responses={"401": CustomExceptionHelper.get_exception_response(UnauthorizedException, "Unauthorized")},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user_by_id(request: Request):
    return await UserService().get_user_by_id(id=request.user.id)


@user_router.post(
    "/register",
    response_model=RegisterResponseSchema,
    responses={"400": CustomExceptionHelper.get_exception_response(DuplicateEmailException, "Email already exist"),
               "400": CustomExceptionHelper.get_exception_response(InvalidEmailException, "Invalid email"),
               "400": CustomExceptionHelper.get_exception_response(InvalidPasswordException, "Invalid password")},
)
async def register(body: RegisterRequestSchema):
    return await UserService().register_user(**body.dict())


@user_router.post(
    "/login",
    response_model=LoginResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"), 
               "401": CustomExceptionHelper.get_exception_response(PasswordDoesNotMatchException, "Password does not match"), 
               "403": CustomExceptionHelper.get_exception_response(EmailNotVerifiedException, "Email not verified"),
    },
)
async def login(body: LoginRequestSchema):
    token = await UserService().login(**body.dict())
    return {"token": token.token, "refresh_token": token.refresh_token}


@user_router.post(
    "/verify-otp",
    response_model=VerifyOTPResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
               "403": CustomExceptionHelper.get_exception_response(EmailAlreadyVerifiedException, "Email already verified"),
               "400": CustomExceptionHelper.get_exception_response(ExpiredOTPException, "OTP expired"),
               "400": CustomExceptionHelper.get_exception_response(WrongOTPException, "Wrong OTP"),
               "401": CustomExceptionHelper.get_exception_response(UnauthorizedException, "Unauthorized")
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailNotVerified]))],
)
async def verify_otp(request: Request, body: VerifyOTPRequestSchema):
    return await UserService().verify_otp(user_id=request.user.id, **body.dict())


@user_router.post(
    "/resend-otp",
    response_model=ResendOTPResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
               "403": CustomExceptionHelper.get_exception_response(EmailAlreadyVerifiedException, "Email already verified"),
               "401": CustomExceptionHelper.get_exception_response(UnauthorizedException, "Unauthorized")
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailNotVerified]))],
)
async def resend_otp(request: Request):
    return await UserService().resend_otp(user_id=request.user.id)


@user_router.post(
    "/verify-email",
    response_model=VerifyEmailResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
               "403": CustomExceptionHelper.get_exception_response(EmailAlreadyVerifiedException, "Email already verified")
    },
)
async def verify_email(body: VerifyEmailRequestSchema):
    return await UserService().verify_email(**body.dict())


@user_router.post(
    "/forgot-password/send-otp",
    response_model=SendForgotPasswordOTPResponseSchema,
    responses={ "404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
                "403": CustomExceptionHelper.get_exception_response(EmailNotVerifiedException, "Email not verified"),
                "429": CustomExceptionHelper.get_exception_response(ForgotPasswordOTPAlreadySentException, "OTP already sent"),
    },
)
async def send_forgot_password_otp(body: SendForgotPasswordOTPRequestSchema):
    return await UserService().send_forgot_password_otp(**body.dict())


@user_router.post(
    "/forgot-password/verify-otp",
    response_model=VerifyForgotPasswordOTPResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
                "403": CustomExceptionHelper.get_exception_response(EmailNotVerifiedException, "Email not verified"),
                "400": CustomExceptionHelper.get_exception_response(ExpiredOTPException, "OTP expired"),
                "400": CustomExceptionHelper.get_exception_response(WrongOTPException, "Wrong OTP"),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified, IsForgotPasswordOtpNotVerified]))],
)
async def verify_forgot_password_otp(request: Request, body: VerifyForgotPasswordOTPRequestSchema):
    return await UserService().verify_forgot_password_otp(user_id=request.user.id, **body.dict())

@user_router.post(
    "/change-password",
    response_model=ChangePasswordResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
                "403": CustomExceptionHelper.get_exception_response(EmailNotVerifiedException, "Email not verified"),
                "400": CustomExceptionHelper.get_exception_response(InvalidPasswordException, "Invalid password"),
                "403": CustomExceptionHelper.get_exception_response(ForgotPasswordOTPNotVerifiedException, "Forgot password OTP not verified"),
                "409": CustomExceptionHelper.get_exception_response(TokenAlreadyUsedException, "Token already used")
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified, IsForgotPasswordOtpVerified]))],
)
async def change_password(request: Request, body: ChangePasswordRequestSchema):
    return await UserService().change_password(user_id=request.user.id, **body.dict())

@user_router.post(
    "/forgot-password/resend-otp",
    response_model=ResendForgotPasswordOTPResponseSchema,
    responses={"404": CustomExceptionHelper.get_exception_response(UserNotFoundException, "User not found"),
                "403": CustomExceptionHelper.get_exception_response(EmailNotVerifiedException, "Email not verified"),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified, IsForgotPasswordOtpNotVerified]))],
)
async def resend_forgot_password_otp(request: Request):
    return await UserService().resend_forgot_password_otp(user_id=request.user.id)