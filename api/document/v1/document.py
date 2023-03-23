from tika import parser
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.elastic import EsClient
from app.elastic.schemas import ElasticDocumentIndexedResponse
from app.exception import BaseHttpErrorSchema
from core.exceptions.base import CustomException

document_router = APIRouter(
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

# TODO: This is temporary.
INDEX_NAME = "search-document-0001"

@document_router.post(
  "/upload",
  description="Upload a document and index it in Elasticsearch (Temporary)",
  response_model=ElasticDocumentIndexedResponse,
  responses= {
    400: {
      "model": BaseHttpErrorSchema,
      "description": "Bad request, please check request body, params, headers, or query"
    }
  }
)
async def upload_document(file: UploadFile = File(...)):
  try :
    parsed_file = parser.from_buffer(file.file.read())
    file_content = parsed_file["content"]
    return EsClient.index_doc(index= INDEX_NAME, doc={"content": file_content})
  except CustomException as e:
    raise HTTPException(
      status_code= e.error_code,
      detail=e.message,
    )