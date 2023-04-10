from fastapi import APIRouter

from api.user.v1.user import user_router as user_v1_router
from api.auth.auth import auth_router
from api.elastic.v1.elastic import elastic_router
from api.document.v1.document import document_router
from api.entity.v1.entity import entity_router
from api.search.v1.search import search_router

router = APIRouter()
router.include_router(user_v1_router, prefix="/api/v1/users", tags=["User"])
router.include_router(document_router, prefix="/api/v1/documents", tags=["Document"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(elastic_router, prefix="/elastic", tags=["Elastic"])
router.include_router(entity_router, prefix="/api/v1/entities", tags=["Entity"])
router.include_router(search_router, prefix="/api/v1/search", tags=["Search"])

__all__ = ["router"]
