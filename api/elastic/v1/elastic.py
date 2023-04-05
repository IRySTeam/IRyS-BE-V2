from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body

from core.exceptions.base import CustomException
from app.exception import BaseHttpErrorSchema
from app.elastic import EsClient
from app.elastic.schemas import (
  ElasticInfo, 
  ElasticIndexCat, 
  ElasticIndexDetail,
  ElasticCreateIndexResponse,
  ElasticDocumentIndexedResponse,
  IndexNamePathParams,
  GetAllIndexQueryParams,  
  CreateIndexBody,
  UpdateIndexBody,
  ElasticIndexUpdateResponse,
  ElasticIndexDeleteResponse
)

elastic_router = APIRouter(
  responses={
    401: {
      "model": BaseHttpErrorSchema,
      "description": "Unauthorized access to elasticsearch or application"
    },
    403: {
      "model": BaseHttpErrorSchema,
      "description": "Forbidden access to elasticsearch or application"
    },
    424: {
      "model": BaseHttpErrorSchema,
      "description": "Failed happened in Elasticsearch or when connecting to Elasticsearch"
    }
  }
)

@elastic_router.get(
  "/info",
  description="Get information about the Elasticsearch cluster",
  response_model=ElasticInfo,
)
async def get_elastic_info():
  try :
    return EsClient.info()
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.get(
  "/indices",
  description="List indices in Elasticsearch",
  response_model=List[ElasticIndexCat],
)
async def get_elastic_indices(query: GetAllIndexQueryParams = Depends()):
  try :
    return EsClient.list_indices(all=query.all)
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.get(
  "/indices/{index_name}",
  description="Get an index in Elasticsearch",
  response_model=ElasticIndexDetail,
  responses = {
    400: {
      "model": BaseHttpErrorSchema,
      "description": "Bad request, please check request body, params, headers, or query"
    },
    404: {
      "model": BaseHttpErrorSchema,
      "description": "Index with the given name does not exist"
    },
  }
)
async def get_elastic_index(path: IndexNamePathParams = Depends()):
  try :
    return EsClient.get_index(path.index_name)
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.post(
  "/indices",
  description="Create an index in Elasticsearch",
  response_model=ElasticCreateIndexResponse,
  responses = {
    400: {
      "model": BaseHttpErrorSchema,
      "description": "Bad request, please check request body, params, headers, or query"
    },
  }
)
async def create_elastic_index(body: CreateIndexBody):
  try :
    return(EsClient.create_index(
      index_name=body.index_name,
      mapping=body.mappings,
      settings=body.settings,
    ))
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.post(
  "/indices/{index_name}/update",
  description="Update an index dynamic settings in Elasticsearch",
  response_model=ElasticIndexUpdateResponse,
  responses = {
    400: {
      "model": BaseHttpErrorSchema,
      "description": "Bad request, please check request body, params, headers, or query"
    },
    404: {
      "model": BaseHttpErrorSchema,
      "description": "Index with the given name does not exist"
    },
  }
)
async def update_elastic_index(body: UpdateIndexBody, path: IndexNamePathParams = Depends()):
  try :
    EsClient.update_index(index=path.index_name, settings=body.settings)
    return ElasticIndexUpdateResponse(updated=True)
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.post(
  "/indices/{index_name}/delete",
  description="Delete an index in Elasticsearch",
  response_model=ElasticIndexDeleteResponse,
  responses = {
    400: {
      "model": BaseHttpErrorSchema,
      "description": "Bad request, please check request body, params, headers, or query"
    },
    404: {
      "model": BaseHttpErrorSchema,
      "description": "Index with the given name does not exist"
    },
  }
)
async def delete_elastic_index(path: IndexNamePathParams = Depends()):
  try :
    EsClient.delete_index(path.index_name)
    return ElasticIndexDeleteResponse(deleted=True)
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.get(
  "/indices/{index_name}/documents",
  description="Get all documents in an index in Elasticsearch",
  responses = {
    404: {
      "model": BaseHttpErrorSchema,
      "description": "Index with the given name does not exist"
    }
  }
)
async def get_all_index_documents(path: IndexNamePathParams = Depends()):
  try :
    return EsClient.list_index_docs(path.index_name)
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )

@elastic_router.post(
  "/indices/{index_name}/documents",
  description="Index a document in Elasticsearch",
  response_model=ElasticDocumentIndexedResponse,
  responses={
    400: {
      "model": BaseHttpErrorSchema,
      "description": "Bad request, please check request body, params, headers, or query"
    },
    404: {
      "model": BaseHttpErrorSchema,
      "description": "Index with the given name does not exist"
    }
  }
)
async def index_document(
  body: Dict[str, Any] = Body(..., description="Document to index"),
  path: IndexNamePathParams = Depends()
):
  try :
    return EsClient.index_doc(index=path.index_name, doc=body)
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )  
  

