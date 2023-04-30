from typing import List

from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.document.schemas import DocumentResponseSchema
from app.document.services import DocumentService
from core.exceptions import (
    EmailNotVerifiedException,
    RepositoryNotFoundException,
    UnauthorizedException,
    UserNotAllowedException,
)
from core.exceptions.base import BadRequestException, NotFoundException
from core.fastapi.dependencies import (
    IsAuthenticated,
    IsEmailVerified,
    PermissionDependency,
)
from core.utils import CustomExceptionHelper

repository_document_router = APIRouter(
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
    }
)


@repository_document_router.post(
    "/{repository_id}/documents/upload",
    description="Upload a document and index it in Elasticsearch",
    response_model=DocumentResponseSchema,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Repository with specified ID does not found",
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def upload_document(
    request: Request, repository_id: int, file: UploadFile = File(...)
):
    return await DocumentService().upload_document(
        user_id=request.user.id, repository_id=repository_id, file=file
    )


@repository_document_router.post(
    "/{repository_id}/documents/uploads",
    response_model=List[DocumentResponseSchema],
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Repository with specified ID does not found",
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def upload_multiple_document(
    request: Request, repository_id: int, files: List[UploadFile]
):
    return await DocumentService().upload_multiple_document(
        user_id=request.user.id, repository_id=repository_id, files=files
    )


@repository_document_router.get(
    "/{repository_id}/documents",
    response_model=List[DocumentResponseSchema],
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_repository_documents(
    request: Request,
    repository_id: int,
):
    return await DocumentService().get_repository_documents(
        user_id=request.user.id, repository_id=repository_id
    )
