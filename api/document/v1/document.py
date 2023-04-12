from binascii import b2a_base64
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from app.exception import BaseHttpErrorSchema
from core.db.session import get_session_context
from core.exceptions.base import CustomException
from celery_app import parsing
from app.document.services import document_service
from app.document.schemas import (
    DocumentResponseSchema,
    IncludeIndexQueryParams,
    DocumentPathParams,
)

document_router = APIRouter(
    responses={
        401: {
            "model": BaseHttpErrorSchema,
            "description": "Unauthorized access to application resources",
        },
        403: {
            "model": BaseHttpErrorSchema,
            "description": "Forbidden access to application resources",
        },
    }
)


@document_router.get(
    "",
    description="Get all documents",
    response_model=List[DocumentResponseSchema],
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        }
    },
)
async def get_all_documents(query: IncludeIndexQueryParams = Depends()):
    try:
        documents = await document_service.get_document_list(
            include_index=query.include_index
        )
        return documents
    except CustomException as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e.message,
        )


@document_router.get(
    "/{doc_id}",
    response_model=DocumentResponseSchema,
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        },
        404: {"model": BaseHttpErrorSchema, "description": "Document not found"},
    },
)
async def get_document(
    path: DocumentPathParams = Depends(), query: IncludeIndexQueryParams = Depends()
):
    try:
        document = await document_service.get_document_by_id(
            id=path.doc_id, include_index=query.include_index
        )
        return document
    except CustomException as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e.message,
        )


@document_router.post(
    "/upload",
    description="Upload a document and index it in Elasticsearch (Temporary)",
    response_model=DocumentResponseSchema,
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        }
    },
)
async def upload_document(file: UploadFile = File(...)):
    # Get file type.
    try:
        # TODO: Is this the correct way to get the title?
        title = ".".join(file.filename.split(".")[:-1])
        document = DocumentResponseSchema.from_orm(
            await document_service.create_document(title=title)
        )
        # TODO: Add with OCR choice.
        # TODO: Add check duplicate.
        parsing.delay(
            document_id=document.id,
            document_title=title,
            file_content_str=b2a_base64(file.file.read()).decode("utf-8"),
        )
        return document
    except CustomException as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e.message,
        )
