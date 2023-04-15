from fastapi import APIRouter, Depends, Query, Request

from app.repository.schemas import (
    CreateRepositoryRequestSchema,
    CreateRepositoryResponseSchema,
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
