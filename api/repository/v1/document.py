from typing import List

from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.document.schemas import (
    DocumentDetailResponseSchema,
    DocumentResponseSchema,
)
from app.document.schemas.request import EditRepositoryDocumentRequestSchema
from app.document.services import DocumentService
from app.repository.schemas import (
    AllDocumentDatabaseResponseSchema,
    DocumentIdPathParams,
    RepositoryIdPathParams,
)
from app.repository.schemas.request import DocumentDatabaseQueryParams
from app.repository.schemas.response import (
    CountResponseSchema,
    MessageResponseSchema,
)
from core.exceptions import (
    EmailNotVerifiedException,
    RepositoryNotFoundException,
    UnauthorizedException,
    UserNotAllowedException,
)
from core.exceptions.base import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from core.exceptions.document import DocumentNotFoundException
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
    "/documents/{doc_id}",
    description="Get a document by ID including metadata and content",
    response_model=DocumentDetailResponseSchema,
    responses={
        "403": CustomExceptionHelper.get_exception_response(
            ForbiddenException, "Document indexing is not finished yet"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            DocumentNotFoundException, "Document not found"
        ),
    },
)
async def get_repo_document_by_id(
    request: Request,
    path: DocumentIdPathParams = Depends(),
):
    return await DocumentService().get_repository_document_by_id(
        doc_id=path.doc_id,
        user_id=request.user.id,
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


@repository_document_router.post(
    "/documents/{doc_id}/edit",
    response_model=MessageResponseSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def edit_repository_document(
    request: Request,
    body: EditRepositoryDocumentRequestSchema,
    path: DocumentIdPathParams = Depends(),
):
    await DocumentService().edit_repository_document(
        user_id=request.user.id,
        document_id=path.doc_id,
        name=body.name,
        category=body.category,
        is_public=body.is_public,
    )

    return MessageResponseSchema(message="Successful")


@repository_document_router.post(
    "/documents/{doc_id}/delete",
    description="Cascade delete a document",
    response_model=MessageResponseSchema,
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            DocumentNotFoundException, "Document not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def delete_repository_document_by_id(
    request: Request,
    path: DocumentIdPathParams = Depends(),
):
    await DocumentService().delete_repository_document(
        user_id=request.user.id,
        document_id=path.doc_id,
    )
    return MessageResponseSchema(message="Document deleted successfully")


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
