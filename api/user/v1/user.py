from typing import List

from fastapi import APIRouter, Depends, Query, Request

from api.user.v1.request.user import LoginRequest
from api.user.v1.response.user import LoginResponse
from app.user.schemas import (
    ExceptionResponseSchema,
    GetUserByIdResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    VerifyOTPRequestSchema,
    VerifyOTPResponseSchema
)
from app.user.services import UserService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
    IsEmailNotVerified
)

user_router = APIRouter()

@user_router.get(
    "/me",
    response_model=GetUserByIdResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user_by_id(request: Request):
    return await UserService().get_user_by_id(id=request.user.id)


@user_router.post(
    "/register",
    response_model=RegisterResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def register(body: RegisterRequestSchema):
    return await UserService().register_user(**body.dict())


@user_router.post(
    "/login",
    response_model=LoginResponse,
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(body: LoginRequest):
    token = await UserService().login(**body.dict())
    return {"token": token.token, "refresh_token": token.refresh_token}


@user_router.post(
    "/verify-otp",
    response_model=VerifyOTPResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}, "404": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailNotVerified]))],
)
async def verify_otp(request: Request, body: VerifyOTPRequestSchema):
    return await UserService().verify_otp(user_id=request.user.id, **body.dict())
