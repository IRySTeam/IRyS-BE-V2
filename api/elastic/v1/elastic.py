from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends

from app.elastic import EsClient
from app.elastic.configuration import (
    GENERAL_ELASTICSEARCH_INDEX_MAPPINGS,
    GENERAL_ELASTICSEARCH_INDEX_SETTINGS,
    RECRUITMENT_ELASTICSEARCH_INDEX_MAPPINGS,
    RECRUITMENT_ELASTICSEARCH_INDEX_SETTINGS,
    SCIENTIFIC_ELASTICSEARCH_INDEX_MAPPINGS,
    SCIENTIFIC_ELASTICSEARCH_INDEX_SETTINGS,
)
from app.elastic.schemas import (
    CreateIndexBody,
    DocDetailPathParams,
    ElasticCreateIndexResponse,
    ElasticDocumentIndexedResponse,
    ElasticIndexCat,
    ElasticIndexDeleteResponse,
    ElasticIndexDetail,
    ElasticIndexUpdateResponse,
    ElasticInfo,
    GetAllIndexQueryParams,
    IndexNamePathParams,
    IndexType,
    UpdateIndexBody,
)
from app.elastic.schemas.document import MessageResponseSchema
from core.exceptions import (
    BadRequestException,
    FailedDependencyException,
    NotFoundException,
    UnauthorizedException,
)
from core.exceptions.user import EmailNotVerifiedException
from core.fastapi.dependencies.permission import (
    IsAuthenticated,
    IsEmailVerified,
    PermissionDependency,
)
from core.utils import CustomExceptionHelper

elastic_router = APIRouter(
    responses={
        "401": CustomExceptionHelper.get_exception_response(
            UnauthorizedException, "Unauthorized"
        ),
        "403": CustomExceptionHelper.get_exception_response(
            EmailNotVerifiedException, "Email not verified"
        ),
        "424": CustomExceptionHelper.get_exception_response(
            FailedDependencyException,
            "Failed happened in Elasticsearch or when connecting to Elasticsearch",
        ),
    }
)


@elastic_router.get(
    "/info",
    description="Get information about the Elasticsearch cluster",
    response_model=ElasticInfo,
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_elastic_info():
    return EsClient.info()


@elastic_router.get(
    "/indices",
    description="List indices in Elasticsearch",
    response_model=List[ElasticIndexCat],
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_elastic_indices(query: GetAllIndexQueryParams = Depends()):
    return EsClient.list_indices(all=query.all)


@elastic_router.get(
    "/indices/{index_name}",
    description="Get an index in Elasticsearch",
    response_model=ElasticIndexDetail,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException, "Index with given name does not exist"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_elastic_index(path: IndexNamePathParams = Depends()):
    return EsClient.get_index(path.index_name)


@elastic_router.post(
    "/indices",
    description="Create an index in Elasticsearch",
    response_model=ElasticCreateIndexResponse,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        )
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def create_elastic_index(body: CreateIndexBody):
    settings = body.settings
    mappings = body.mappings

    if body.index_type == IndexType.GENERAL.value:
        settings = GENERAL_ELASTICSEARCH_INDEX_SETTINGS
        mappings = GENERAL_ELASTICSEARCH_INDEX_MAPPINGS
    elif body.index_type == IndexType.SCIENTIFIC.value:
        settings = SCIENTIFIC_ELASTICSEARCH_INDEX_SETTINGS
        mappings = SCIENTIFIC_ELASTICSEARCH_INDEX_MAPPINGS
    elif body.index_type == IndexType.RECRUITMENT.value:
        settings = RECRUITMENT_ELASTICSEARCH_INDEX_SETTINGS
        mappings = RECRUITMENT_ELASTICSEARCH_INDEX_MAPPINGS

    return EsClient.create_index(
        index_name=body.index_name,
        mappings=mappings,
        settings=settings,
    )


@elastic_router.post(
    "/indices/{index_name}/update",
    description="Update an index dynamic settings in Elasticsearch",
    response_model=ElasticIndexUpdateResponse,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException, "Index with given name does not exist"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def update_elastic_index(
    body: UpdateIndexBody, path: IndexNamePathParams = Depends()
):
    EsClient.update_index(index=path.index_name, settings=body.settings)
    return ElasticIndexUpdateResponse(updated=True)


@elastic_router.post(
    "/indices/{index_name}/delete",
    description="Delete an index in Elasticsearch",
    response_model=ElasticIndexDeleteResponse,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException, "Index with given name does not exist"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def delete_elastic_index(path: IndexNamePathParams = Depends()):
    EsClient.delete_index(path.index_name)
    return ElasticIndexDeleteResponse(deleted=True)


@elastic_router.get(
    "/indices/{index_name}/documents",
    description="Get all documents in an index in Elasticsearch",
    responses={
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException, "Index with given name does not exist"
        )
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def get_all_index_documents(path: IndexNamePathParams = Depends()):
    return EsClient.list_index_docs(path.index_name)


@elastic_router.post(
    "/indices/{index_name}/documents",
    description="Index a document in Elasticsearch",
    response_model=ElasticDocumentIndexedResponse,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException, "Index with given name does not exist"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def index_document(
    body: Dict[str, Any] = Body(..., description="Document to index"),
    path: IndexNamePathParams = Depends(),
):
    return EsClient.index_doc(index=path.index_name, doc=body)


@elastic_router.post(
    "/indices/{index_name}/documents/{doc_id}/delete",
    description="Delete a document in Elasticsearch",
    response_model=MessageResponseSchema,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Document with given elasticsearch index name and id does not exist",
        ),
    },
)
async def delete_document(
    path: DocDetailPathParams = Depends(),
):
    EsClient.delete_doc(index=path.index_name, doc_id=path.doc_id)
    return MessageResponseSchema(message="Document deleted successfully")


@elastic_router.post(
    "/indices/{index_name}/documents/{doc_id}/update",
    description="Update a document in Elasticsearch",
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            BadRequestException,
            "Bad request, please check request body, params, headers, or query",
        ),
        "404": CustomExceptionHelper.get_exception_response(
            NotFoundException,
            "Document with given elasticsearch index name and id does not exist",
        ),
    },
)
async def update_document(
    body: Dict[str, Any] = Body(..., description="Document to update"),
    path: DocDetailPathParams = Depends(),
):
    return EsClient.update_doc(index=path.index_name, doc_id=path.doc_id, doc=body)
