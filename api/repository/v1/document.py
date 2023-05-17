from typing import List

from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.document.schemas import DocumentResponseSchema
from app.document.services import DocumentService
from app.repository.schemas import (
    AllDocumentDatabaseResponseSchema,
    CountResponseSchema,
    DocumentDatabaseQueryParams,
    RepositoryIdPathParams,
)
from core.exceptions import (
    BadRequestException,
    EmailNotVerifiedException,
    NotFoundException,
    RepositoryNotFoundException,
    UnauthorizedException,
    UserNotAllowedException,
)
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
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
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
)
async def upload_document(
    request: Request,
    path: RepositoryIdPathParams = Depends(),
    file: UploadFile = File(...),
):
    return await DocumentService().upload_document(
        user_id=request.user.id, repository_id=path.repository_id, file=file
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
)
async def upload_multiple_document(
    request: Request,
    files: List[UploadFile],
    path: RepositoryIdPathParams = Depends(),
):
    return await DocumentService().upload_multiple_document(
        user_id=request.user.id, repository_id=path.repository_id, files=files
    )


@repository_document_router.get(
    "/{repository_id}/documents/count",
    description="Get the number of documents in a repository",
    response_model=CountResponseSchema,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
)
async def get_repository_documents_count(
    request: Request,
    path: RepositoryIdPathParams = Depends(),
):
    return CountResponseSchema(
        count=await DocumentService().get_repository_documents_count(
            user_id=request.user.id,
            repository_id=path.repository_id,
        )
    )


@repository_document_router.get(
    "/{repository_id}/documents/database",
    description="Get the database of documents in a repository",
    response_model=AllDocumentDatabaseResponseSchema,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_repository_documents_database(
    request: Request,
    path: RepositoryIdPathParams = Depends(),
    query: DocumentDatabaseQueryParams = Depends(),
):
    return await DocumentService().get_document_database(
        user_id=request.user.id,
        repository_id=path.repository_id,
        page_size=query.page_size,
        page_no=query.page_no,
        find_document=query.find_document,
    )
