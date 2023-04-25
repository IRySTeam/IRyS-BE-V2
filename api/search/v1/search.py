import json

from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from app.search.services.search import SearchService
from app.search.enums.search import DomainEnum
from app.search.schemas.search import SemanticSearchRequest, SemanticSearchResponseSchema
from app.exception import BaseHttpErrorSchema

from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
)

search_router = APIRouter()
ss = SearchService(None, None, None)


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
    return ss.run_search(request.query, request.domain, request.advanced_filter)

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
