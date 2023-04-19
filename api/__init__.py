from fastapi import APIRouter

from api.user.v1.user import user_router as user_v1_router
from api.auth.auth import auth_router
from api.elastic.v1.elastic import elastic_router
from api.document.v1.document import document_router
from api.repository.v1.repository import repository_router
from api.extraction.v1.extraction import extraction_router

router = APIRouter()
router.include_router(user_v1_router, prefix="/api/v1/users", tags=["User"])
router.include_router(document_router, prefix="/api/v1/documents", tags=["Document"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(elastic_router, prefix="/elastic", tags=["Elastic"])
router.include_router(
    repository_router, prefix="/api/v1/repositories", tags=["Repository"]
)
router.include_router(extraction_router, prefix="/extraction", tags=["Extraction"])

__all__ = ["router"]
