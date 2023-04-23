from binascii import b2a_base64
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form

from app.exception import BaseHttpErrorSchema
from core.exceptions.base import CustomException
from core.utils import CustomExceptionHelper
from core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    FailedDependencyException,
    NotFoundException,
)
from celery_app import parsing, celery
from app.elastic import EsClient
from app.document.enums.document import IndexingStatusEnum
from app.document.models import Document
from app.document.services import document_service, document_index_service
from app.document.schemas import (
    DocumentResponseSchema,
    IncludeIndexQueryParams,
    DocumentPathParams,
    ReindexDocumentResponse,
)

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
async def upload_document(repository_id: int = Form(...), file: UploadFile = File(...)):
    document: Document = None
    try:
        file_bytes = file.file.read()
        # TODO: Use information extraction to extract title.
        title = ".".join(file.filename.split(".")[:-1])
        file_content_str = b2a_base64(file_bytes).decode("utf-8")
        doc_id = await document_service.create_document(
            title=title,
            repository_id=repository_id,
            file_content_str=file_content_str,
        )
        document = await document_service.get_document_by_id(
            id=doc_id, include_index=True
        )
        parsing.delay(
            document_id=document.id,
            document_title=title,
            file_content_str=file_content_str,
        )
        return document
    except Exception as e:
        # Delete the document if there is an error.
        if document:
            await document_service.delete_document(document.id)
        raise e


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
