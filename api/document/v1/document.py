from typing import List

from fastapi import APIRouter, Depends

from app.document.schemas import (
    DocumentResponseSchema,
    IncludeIndexQueryParams,
)
from app.document.services import document_service
from core.exceptions import BadRequestException, UnauthorizedException
from core.exceptions.user import EmailNotVerifiedException
from core.fastapi.dependencies.permission import (
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
    }
)


@document_router.get(
    "",
    description="Get all documents",
    response_model=List[DocumentResponseSchema],
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        )
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_all_documents(query: IncludeIndexQueryParams = Depends()):
    documents = await document_service.get_document_list(
        include_index=query.include_index
    )
    return [doc.__dict__ for doc in documents]
