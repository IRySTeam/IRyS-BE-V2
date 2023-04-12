from fastapi import APIRouter, Depends, Query, Request

from app.repository.schemas import (
    CreateRepositoryRequestSchema,
    CreateRepositoryResponseSchema
)
from app.repository.services import RepositoryService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
    IsEmailVerified,
)

repository_router = APIRouter()

@repository_router.post(
    "/create",
    response_model=CreateRepositoryResponseSchema,
    responses={
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def create_repository(request: Request, body: CreateRepositoryRequestSchema):
    return await RepositoryService().create_repository(user_id=request.user.id, **body.dict())