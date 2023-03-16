from typing import List

from fastapi import APIRouter, Depends, Query

from api.user.v1.request.user import LoginRequest
from api.user.v1.response.user import LoginResponse
from app.user.schemas import (
    ExceptionResponseSchema,
    GetUserListResponseSchema,
    GetUserByIdResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
)
from app.user.services import UserService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
)

user_router = APIRouter()


@user_router.get(
    "",
    response_model=List[GetUserListResponseSchema],
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    prev: int = Query(None, description="Prev ID"),
):
    return await UserService().get_user_list(limit=limit, prev=prev)


@user_router.get(
    "/{id}",
    response_model=GetUserByIdResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user_by_id(id: int):
    return await UserService().get_user_by_id(id=id)


@user_router.post(
    "/register",
    response_model=RegisterResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def register(request: RegisterRequestSchema):
    await UserService().create_user(**request.dict())
    return {"email": request.email, "first_name": request.first_name, "last_name": request.last_name}


@user_router.post(
    "/login",
    response_model=LoginResponse,
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(request: LoginRequest):
    token = await UserService().login(email=request.email, password=request.password)
    return {"token": token.token, "refresh_token": token.refresh_token}
