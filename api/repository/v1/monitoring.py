from fastapi import APIRouter, Depends, Request

from app.document.services import DocumentService
from app.repository.schemas import (
    MessageResponseSchema,
    MonitorAllDocumentPathParams,
    MonitorAllDocumentQueryParams,
    MonitorAllDocumentResponseSchema,
    ReindexAllDocumentPathParams,
    ReindexDocumentPathParams,
)
from app.repository.services import RepositoryService
from core.exceptions import (
    EmailNotVerifiedException,
    UnauthorizedException,
    UserNotAllowedException,
)
from core.exceptions.base import NotFoundException
from core.exceptions.repository import RepositoryNotFoundException
from core.fastapi.dependencies import (
    IsAuthenticated,
    IsEmailVerified,
    PermissionDependency,
)
from core.utils import CustomExceptionHelper

monitoring_router = APIRouter(
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
            RepositoryNotFoundException, "Repository with specified id not found"
        ),
    }
)


@monitoring_router.get(
    "/{repository_id}/monitor",
    response_model=MonitorAllDocumentResponseSchema,
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def monitor_repository_documents(
    request: Request,
    path: MonitorAllDocumentPathParams = Depends(),
    query: MonitorAllDocumentQueryParams = Depends(),
):
    return await DocumentService().monitor_all_document(
        user_id=request.user.id,
        repository_id=path.repository_id,
        status=query.status,
        page_size=query.page_size,
        page_no=query.page_no,
    )


@monitoring_router.get(
    "/documents/{doc_id}/reindex",
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
async def reindex_document(
    request: Request, path: ReindexDocumentPathParams = Depends()
):
    await DocumentService().reindex_by_id(doc_id=path.doc_id, user_id=request.user.id)
    return MessageResponseSchema(
        message="Document reindexing has been started",
    )


@monitoring_router.post(
    "/{repository_id}/documents/reindex",
    response_model=MessageResponseSchema,
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def reindex_all(
    request: Request,
    path: ReindexAllDocumentPathParams = Depends(),
):
    await RepositoryService().reindex_all(
        repository_id=path.repository_id,
        user_id=request.user.id,
    )
    return MessageResponseSchema(
        message="All documents reindexing has been started",
    )
