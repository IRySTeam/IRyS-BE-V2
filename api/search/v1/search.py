import pandas as pd

from fastapi import Depends, APIRouter, File, UploadFile, Request
from app.document.services.document import DocumentService
from app.exception import BaseHttpErrorSchema
from app.preprocess import PreprocessUtil
from app.search.enums.search import DomainEnum
from app.search.schemas.search import (
    DocumentDetails,
    SemanticSearchRequest,
    SemanticSearchResponseSchema,
    RepoSearchPathParams,
    FileSearchPathParams,
)
from core.exceptions import (
    EmailNotVerifiedException,
    InvalidRepositoryCollaboratorException,
    InvalidRepositoryRoleException,
    RepositoryNotFoundException,
    UnauthorizedException,
    UserNotAllowedException,
)
from core.utils import CustomExceptionHelper
from core.fastapi.dependencies import (
    IsAuthenticated,
    IsEmailVerified,
    PermissionDependency,
)
from app.search.services.search import SearchService

search_router = APIRouter()
ss = SearchService(None, None, None)
ds = DocumentService()

@search_router.post(
    "/public",
    description="Fetches relevant public documents",
    response_model=SemanticSearchResponseSchema,        
    responses={
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def search_public(
        request: Request,
        body: SemanticSearchRequest
    ):
    doc_ids = await DocumentService().get_all_accessible_documents(request.user.id)

    result = ss.run_search(
        body.query, body.domain, body.advanced_filter, doc_ids
    )
    retrieved_doc_ids = [doc.get("id") for doc in result]
    retrieved_doc_ids = pd.Series(retrieved_doc_ids).drop_duplicates().tolist()
    
    result_list = []
    if (retrieved_doc_ids):
        retrieved_doc_details = await DocumentService().get_document_by_ids(
            retrieved_doc_ids
        )
        for i in range(len(retrieved_doc_ids)):
            result_list.append(
                DocumentDetails(
                    details=retrieved_doc_details[i].__dict__,
                    preview=f"...{result[i].get('text')}...",
                    highlights=PreprocessUtil().preprocess(body.query),
                )
            )

    return SemanticSearchResponseSchema(
        num_docs_retrieved=len(retrieved_doc_ids),
        result=result_list,
    )

@search_router.post(
    "/repository/{repository_id}",
    description="Fetches relevant public documents",
    response_model=SemanticSearchResponseSchema,
    responses={
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def search_repo(
        request: Request,
        path: RepoSearchPathParams,
        body: SemanticSearchRequest
    ):
    doc_ids = await DocumentService().get_repo_accessible_documents(path.repository_id)
    result = ss.run_search(
        body.query, body.domain, body.advanced_filter, doc_ids
    )
    retrieved_doc_ids = [doc.get("id") for doc in result]
    retrieved_doc_ids = pd.Series(retrieved_doc_ids).drop_duplicates().tolist()
    
    result_list = []
    if (retrieved_doc_ids):
        retrieved_doc_details = await DocumentService().get_document_by_ids(
            retrieved_doc_ids
        )
        for i in range(len(retrieved_doc_ids)):
            result_list.append(
                DocumentDetails(
                    details=retrieved_doc_details[i].__dict__,
                    preview=f"...{result[i].get('text')}...",
                    highlights=PreprocessUtil().preprocess(body.query),
                )
            )

    return SemanticSearchResponseSchema(
        num_docs_retrieved=len(retrieved_doc_ids),
        result=result_list,
    )

@search_router.post(
    "/file/{repository_id}",
    description="Fetch similar documents based on uploaded document",
    response_model=SemanticSearchResponseSchema,
    responses={
        "403": CustomExceptionHelper.get_exception_response(
            UserNotAllowedException, "Not allowed"
        ),
        "404": CustomExceptionHelper.get_exception_response(
            RepositoryNotFoundException, "Repository not found"
        ),
    },
    dependencies=[Depends(PermissionDependency([IsAuthenticated, IsEmailVerified]))],
)
async def upload_document(
        request: Request,
        path: FileSearchPathParams = Depends(),
        file: UploadFile = File(...)):
    doc_ids = await DocumentService().get_repo_accessible_documents(path.repository_id)

    result = ss.run_file_search(file, path.domain, doc_ids)
    retrieved_doc_ids = [doc.get("id") for doc in result]
    retrieved_doc_ids = pd.Series(retrieved_doc_ids).drop_duplicates().tolist()
    
    result_list = []
    if (retrieved_doc_ids):
        retrieved_doc_details = await DocumentService().get_document_by_ids(
            retrieved_doc_ids
        )
        for i in range(len(retrieved_doc_ids)):
            result_list.append(
                DocumentDetails(
                    details=retrieved_doc_details[i].__dict__,
                    preview=f"...{result[i].get('text')}...",
                    highlights=[],
                )
            )

    return SemanticSearchResponseSchema(
        num_docs_retrieved=len(retrieved_doc_ids),
        result=result_list,
    )
