import json

from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from app.search.services.search import SearchService
from app.search.enums.search import DomainEnum
from app.search.schemas.search import SemanticSearchRequest, SemanticSearchResponseSchema, DocumentDetails
from app.document.services.document import DocumentService
from app.document.schemas.document import DocumentResponseSchema
from app.preprocess import PreprocessUtil
from app.exception import BaseHttpErrorSchema

from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
)

search_router = APIRouter()
ss = SearchService(None, None, None)
ds = DocumentService()

@search_router.post(
    "/",
    description="Fetches relevant documents based on search query and advanced filter",
    response_model=SemanticSearchResponseSchema,
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        }
    },
)
async def search(request: SemanticSearchRequest):  
    doc_ids = [16, 17, 18] # TODO: Get from document repo
    doc_details = await DocumentService().get_document_by_ids(doc_ids)

    result = ss.run_search(request.query, request.domain, request.advanced_filter, doc_ids, doc_details)
    retrieved_doc_ids = [doc.get('id') for doc in result]
    retrieved_doc_details = await DocumentService().get_document_by_ids(retrieved_doc_ids)
    
    # doc_dict_list = [doc.__dict__ for doc in retrieved_doc_details]
    result_list = []
    for i in range(len(result)):
        result_list.append(
            DocumentDetails(
                details=retrieved_doc_details[i].__dict__,
                preview=f"...{result[i].get('text')}...",
                highlights=PreprocessUtil().preprocess(request.query)
            )
        )
    
    return SemanticSearchResponseSchema(
        message=f"Successfully retrieved {len(retrieved_doc_ids)} documents",
        result=result_list
    )

@search_router.post(
    "/file",
    description="Fetch similar documents based on uploaded document",
    response_model=SemanticSearchResponseSchema,
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        }
    },
)
async def upload_document(domain: DomainEnum, file: UploadFile = File(...)):
    return ss.run_file_search(file, domain)
