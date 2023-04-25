from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from app.document.schemas import (
    DocumentPathParams,
    DocumentResponseSchema,
    IncludeIndexQueryParams,
    ReindexDocumentResponse,
)
from app.document.services import DocumentService, document_service
from core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from core.utils import CustomExceptionHelper

document_router = APIRouter(
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException,
            "Unauthorized access to application resources",
        ),
        "403": CustomExceptionHelper.get_exception_response(
            ForbiddenException, ForbiddenException.message
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
)
async def get_all_documents(query: IncludeIndexQueryParams = Depends()):
    documents = await document_service.get_document_list(
        include_index=query.include_index
    )
    return [doc.__dict__ for doc in documents]


@document_router.get(
    "/{doc_id}",
    response_model=DocumentResponseSchema,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Document with specified ID does not found",
        ),
    },
)
async def get_document(
    path: DocumentPathParams = Depends(), query: IncludeIndexQueryParams = Depends()
):
    document = await document_service.get_document_by_id(
        id=path.doc_id, include_index=query.include_index
    )
    return document.__dict__


@document_router.post(
    "/upload",
    description="Upload a document and index it in Elasticsearch (Temporary)",
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
async def upload_document(file: UploadFile = File(...)):
    return await DocumentService().create_document(file=file)


@document_router.get(
    "/{doc_id}/reindex",
    response_model=ReindexDocumentResponse,
    description="Reindex a document in Elasticsearch",
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Document with specified ID does not found",
        ),
    },
)
async def reindex_document(path: DocumentPathParams = Depends()):
    await document_service.reindex_by_id(path.doc_id)
    return {
        "success": True,
    }
