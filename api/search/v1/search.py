from typing import List

from fastapi import APIRouter, Depends, Query

from api.search.v1.search import SemanticSearchRequest
from api.search.v1.search import SemanticSearchResponse

from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
)

search_router = APIRouter()

@search_router.get(
    "/search",
    response_model=SemanticSearchResponse,
)
async def search(request: SemanticSearchRequest):
    pass
