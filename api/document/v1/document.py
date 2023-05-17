from typing import List

from fastapi import APIRouter, Depends, Query, Request

from app.document.schemas import (
    AddDocumentCollaboratorRequestSchema,
    DocumentCollaboratorSchema,
    DocumentDetailResponseSchema,
    EditDocumentCollaboratorRequestSchema,
    EditRepositoryDocumentRequestSchema,
    RemoveDocumentCollaboratorRequestSchema,
)
from app.document.services import DocumentService
from app.repository.schemas import DocumentIdPathParams, MessageResponseSchema
from app.user.schemas import SearchUserResponseSchema
from app.user.services import UserService
from core.exceptions import (
    DocumentNotFoundException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    UserNotAllowedException,
)
from core.exceptions.user import EmailNotVerifiedException
from core.fastapi.dependencies import (
    IsAuthenticated,
    IsEmailVerified,
    PermissionDependency,
)
from core.utils import CustomExceptionHelper

document_router = APIRouter(
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            DocumentNotFoundException, "Document not found"
        ),
    }
)


@document_router.get(
    "/{document_id}",
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
        doc_id=path.document_id,
        user_id=request.user.id,
    )


@document_router.post(
    "/{document_id}/edit",
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
        document_id=path.document_id,
        name=body.name,
        category=body.category,
        is_public=body.is_public,
    )

    return MessageResponseSchema(message="Successful")


@document_router.post(
    "/{document_id}/delete",
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
        document_id=path.document_id,
    )
    return MessageResponseSchema(message="Document deleted successfully")


@document_router.get(
    "/{document_id}/collaborators",
    response_model=List[DocumentCollaboratorSchema],
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_document_collaborators(
    request: Request,
    document_id: int,
):
    return await DocumentService().get_document_collaborators(
        user_id=request.user.id,
        document_id=document_id,
    )


@document_router.post(
    "/{document_id}/collaborators/add",
    response_model=MessageResponseSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def add_document_collaborator(
    request: Request,
    document_id: int,
    body: AddDocumentCollaboratorRequestSchema,
):
    await DocumentService().add_document_collaborator(
        user_id=request.user.id,
        document_id=document_id,
        **body.dict(),
    )

    return MessageResponseSchema(message="Successful")


@document_router.post(
    "/{document_id}/collaborators/edit",
    response_model=MessageResponseSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def edit_document_collaborator(
    request: Request,
    document_id: int,
    body: EditDocumentCollaboratorRequestSchema,
):
    await DocumentService().edit_document_collaborator(
        user_id=request.user.id,
        document_id=document_id,
        **body.dict(),
    )

    return MessageResponseSchema(message="Successful")


@document_router.post(
    "/{document_id}/collaborators/remove",
    response_model=MessageResponseSchema,
    responses={},
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def remove_document_collaborator(
    request: Request,
    document_id: int,
    body: RemoveDocumentCollaboratorRequestSchema,
):
    await DocumentService().delete_document_collaborator(
        user_id=request.user.id,
        document_id=document_id,
        **body.dict(),
    )

    return MessageResponseSchema(message="Successful")


@document_router.get(
    "/{document_id}/reindex",
    response_model=MessageResponseSchema,
    description="Reindex a document in Elasticsearch",
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Document with specified ID does not found",
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def reindex_document(request: Request, path: DocumentIdPathParams = Depends()):
    await DocumentService().reindex_by_id(
        doc_id=path.document_id, user_id=request.user.id
    )
    return MessageResponseSchema(
        message="Document reindexing has been started",
    )


@document_router.get(
    "/{repository_id}/collaborators/add/search",
    response_model=SearchUserResponseSchema,
    responses={
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def search_user(
    request: Request,
    repository_id: int,
    query: str = Query("", description="Search query (name or email)"),
    page_no: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Page size"),
):
    return await UserService().search_user_for_repository_collaborator(
        user_id=request.user.id,
        query=query,
        repository_id=repository_id,
        page_no=page_no,
        page_size=page_size,
    )
