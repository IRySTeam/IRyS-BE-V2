import json

from typing import List

from fastapi import APIRouter, Depends, Query

from app.search.services.search import SearchService
from app.search.schemas.search import SemanticSearchRequest

from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
)

search_router = APIRouter()
ss = SearchService(None, None, None)

@search_router.post(
    "/",
    description="Fetches relevant documents based on search query and advanced filter"
)
async def search(request: SemanticSearchRequest):
    return ss.run_search(request.query, request.advanced_filter)
