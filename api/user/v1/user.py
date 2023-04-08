from typing import List

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from api.user.v1.request.user import LoginRequest
from api.user.v1.response.user import LoginResponse
from app.user.schemas import (
    ExceptionResponseSchema,
    GetUserByIdResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    VerifyOTPRequestSchema,
    VerifyOTPResponseSchema,
    ResendOTPResponseSchema,
    VerifyEmailRequestSchema,
    VerifyEmailResponseSchema,
)
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
)
from core.utils import CustomExceptionHelper
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
    IsEmailNotVerified,
)

user_router = APIRouter()


@user_router.get(
    "/me",
    response_model=GetUserByIdResponseSchema,
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        )
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user_by_id(request: Request):
    return await UserService().get_user_by_id(id=request.user.id)


@user_router.post(
    "/register",
    response_model=RegisterResponseSchema,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            DuplicateEmailException, "Email already exist"
        ),
        "400": CustomExceptionHelper.get_exception_response(
            InvalidEmailException, "Invalid email"
        ),
        "400": CustomExceptionHelper.get_exception_response(
            InvalidPasswordException, "Invalid password"
        ),
    },
)
async def register(body: RegisterRequestSchema):
    return await UserService().register_user(**body.dict())


@user_router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            UserNotFoundException, "User not found"
        ),
        "401": CustomExceptionHelper.get_exception_response(
            PasswordDoesNotMatchException, "Password does not match"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
    },
)
async def login(body: LoginRequest):
    token = await UserService().login(**body.dict())
    return {"token": token.token, "refresh_token": token.refresh_token}


@user_router.post(
    "/verify-otp",
    response_model=VerifyOTPResponseSchema,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            UserNotFoundException, "User not found"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailAlreadyVerifiedException, "Email already verified"
        ),
        "400": CustomExceptionHelper.get_exception_response(
            ExpiredOTPException, "OTP expired"
        ),
        "400": CustomExceptionHelper.get_exception_response(
            WrongOTPException, "Wrong OTP"
        ),
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailNotVerified]))],
)
async def verify_otp(request: Request, body: VerifyOTPRequestSchema):
    return await UserService().verify_otp(user_id=request.user.id, **body.dict())


@user_router.post(
    "/resend-otp",
    response_model=ResendOTPResponseSchema,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            UserNotFoundException, "User not found"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailAlreadyVerifiedException, "Email already verified"
        ),
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailNotVerified]))],
)
async def resend_otp(request: Request):
    return await UserService().resend_otp(user_id=request.user.id)


@user_router.post(
    "/verify-email",
    response_model=VerifyEmailResponseSchema,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            UserNotFoundException, "User not found"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailAlreadyVerifiedException, "Email already verified"
        ),
    },
)
async def verify_email(body: VerifyEmailRequestSchema):
    return await UserService().verify_email(**body.dict())
