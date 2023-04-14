from typing import List
from fastapi import APIRouter, Depends, Query, Request

from app.repository.schemas import (
    CreateRepositoryRequestSchema,
    CreateRepositoryResponseSchema,
    GetJoinedRepositoriesSchema,
    GetPublicRepositoriesResponseSchema,
)
from app.repository.services import RepositoryService
from core.exceptions import (
    UnauthorizedException,
    EmailNotVerifiedException,
    RepositoryDetailsEmptyException,
)
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
    IsEmailVerified,
)
from core.utils import CustomExceptionHelper

repository_router = APIRouter()


@repository_router.post(
    "/create",
    response_model=CreateRepositoryResponseSchema,
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "400": CustomExceptionHelper.get_exception_response(
            RepositoryDetailsEmptyException, "Some repository details are empty"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def create_repository(request: Request, body: CreateRepositoryRequestSchema):
    return await RepositoryService().create_repository(
        user_id=request.user.id, **body.dict()
    )


@repository_router.get(
    "/joined",
    response_model=GetJoinedRepositoriesSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_joined_repositories(
    request: Request,
    name: str = Query(None, description="Name"),
    type: str = Query(None, description="Type"),
    sort_by: str = Query(None, description="Sort By"),
    page_no: int = Query(1, description="Page Number"),
    page_size: int = Query(10, description="Page Size"),
):
    return await RepositoryService().get_joined_repositories(
        user_id=request.user.id,
        name=name,
        type=type,
        sort_by=sort_by,
        page_no=page_no,
        page_size=page_size,
    )


@repository_router.get(
    "/public",
    response_model=GetPublicRepositoriesResponseSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_public_repositories(
    name: str = Query(None, description="Name"),
    page_no: int = Query(1, description="Page Number"),
    page_size: int = Query(10, description="Page Size"),
):
    return await RepositoryService().get_public_repositories(
        name=name, page_no=page_no, page_size=page_size
    )
