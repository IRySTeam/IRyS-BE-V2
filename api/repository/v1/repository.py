from typing import List
from fastapi import APIRouter, Depends, Query, Request

from app.repository.schemas import *
from app.repository.services import RepositoryService
from core.exceptions import (
    UnauthorizedException,
    EmailNotVerifiedException,
    RepositoryDetailsEmptyException,
    RepositoryNotFoundException,
    UserNotAllowedException,
    InvalidRepositoryRoleException,
    DuplicateCollaboratorException,
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
    response_model=GetJoinedRepositoriesResponseSchema,
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
    },
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
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
    },
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


@repository_router.post(
    "/{repository_id}/edit",
    response_model=MessageResponseSchema,
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def edit_repository(
    request: Request,
    repository_id: int,
    body: EditRepositoryRequestSchema,
):
    await RepositoryService().edit_repository(
        user_id=request.user.id, repository_id=repository_id, params=body.dict()
    )
    return MessageResponseSchema(message="Successful")


@repository_router.get(
    "/{repository_id}",
    response_model=RepositorySchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_repository_details(request: Request, repository_id: int):
    return await RepositoryService().get_repository_details(
        user_id=request.user.id, repository_id=repository_id
    )


@repository_router.get(
    "/{repository_id}/members",
    response_model=List[RepositoryCollaboratorSchema],
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_repository_collaborators(
    request: Request,
    repository_id: int,
):
    return await RepositoryService().get_repository_collaborators(
        user_id=request.user.id, repository_id=repository_id
    )


@repository_router.post(
    "/{repository_id}/members/add",
    response_model=MessageResponseSchema,
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
        "400": CustomExceptionHelper.get_exception_response(
            InvalidRepositoryRoleException, "Invalid repository role"
        ),
        "422": CustomExceptionHelper.get_exception_response(
            DuplicateCollaboratorException, "Duplicate collaborator"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def add_repository_collaborator(
    request: Request,
    repository_id: int,
    body: AddRepositoryCollaboratorRequestSchema,
):
    await RepositoryService().add_repository_collaborator(
        user_id=request.user.id, repository_id=repository_id, params=body.dict()
    )
    return MessageResponseSchema(message="Successful")


@repository_router.post(
    "/{repository_id}/members/edit",
    response_model=MessageResponseSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def edit_repository_collaborator(
    request: Request,
    repository_id: int,
    body: EditRepositoryCollaboratorRequestSchema,
):
    await RepositoryService().edit_repository_collaborator(
        user_id=request.user.id, repository_id=repository_id, **body.dict()
    )
    return MessageResponseSchema(message="Successful")


@repository_router.post(
    "/{repository_id}/members/remove",
    response_model=MessageResponseSchema,
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def remove_repository_collaborator(
    request: Request,
    repository_id: int,
    body: MessageResponseSchema,
):
    await RepositoryService().remove_repository_collaborator(
        user_id=request.user.id, repository_id=repository_id, params=body.dict()
    )
    return MessageResponseSchema(message="Successful")
