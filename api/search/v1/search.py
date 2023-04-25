from fastapi import APIRouter

from app.search.schemas.search import SemanticSearchRequest
from app.search.services.search import SearchService

search_router = APIRouter()
ss = SearchService(None, None, None)


@search_router.post(
    "/",
    description="Fetches relevant documents based on search query and advanced filter",
)
async def search(request: SemanticSearchRequest):
    return ss.run_search(request.query, request.advanced_filter)
