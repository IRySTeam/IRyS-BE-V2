from fastapi import APIRouter, Depends, Request

from app.document.services import DocumentService
from app.repository.schemas import (
    MonitorAllDocumentPathParams,
    MonitorAllDocumentQueryParams,
    MonitorAllDocumentResponseSchema,
    ReindexAllResponseSchema,
)
from app.repository.services import RepositoryService
from core.exceptions import (
    EmailNotVerifiedException,
    UnauthorizedException,
    UserNotAllowedException,
)
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
    "/{repository_id}/reindex-all",
    response_model=ReindexAllResponseSchema,
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def reindex_all(request: Request, repository_id: int):
    await RepositoryService().reindex_all(
        repository_id=repository_id,
        user_id=request.user.id,
    )
    return {
        "success": True,
    }
