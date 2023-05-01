from dataclasses import dataclass
from datetime import datetime

from fastapi import Path, Query
from pydantic import BaseModel, Field

from app.document.enums.document import IndexingStatusEnum

# ==============================================================================
# Request Body-related Schemas.
# ==============================================================================


# ==============================================================================
# Response Body-related Schemas.
# ==============================================================================
class DocumentIndexing(BaseModel):
    id: int = Field(..., description="Document indexing id")
    doc_id: int = Field(..., description="Corresponding document id")
    status: IndexingStatusEnum = Field(..., description="Indexing status")
    reason: str = Field(None, description="Reason for failure / success message")

    class Config:
        orm_mode = True


class DocumentResponseSchema(BaseModel):
    id: int = Field(..., description="Document id")
    title: str = Field(..., description="Document title")
    file_url: str = Field(..., description="Document file url")
    elastic_doc_id: str = Field(None, description="Document id in Elasticsearch")
    elastic_index_name: str = Field(None, description="Elasticsearch index name")
    created_at: datetime = Field(None, description="Document's created at metadata")
    updated_at: datetime = Field(None, description="Document's updated at metadata")
    is_public: bool = Field(None, description="Document visibility")
    mimetype: str = Field(None, description="Document format")


    class Config:
        orm_mode = True


class MonitorDocumentResponseSchema(BaseModel):
    id: int = Field(..., description="Document id")
    title: str = Field(..., description="Document title")
    updated_at: datetime = Field(None, description="Document's updated at")
    index: DocumentIndexing = Field(None, description="Document indexing status")
    title: str = Field(None, description="Document title")
    created_at: datetime = Field(None, description="Document create time")
    updated_at: datetime = Field(None, description="Document last update time")
    file_url: str = Field(None, description="Document link on GCS")
    is_public: bool = Field(None, description="Document visibility")

    class Config:
        orm_mode = True


class UploadDocumentBody(BaseModel):
    repository_id: int = Field(..., description="Repository id")

    class Config:
        orm_mode = True


class MessageResponseSchema(BaseModel):
    message: str = Field(..., description="Message")


# ==============================================================================
# Path parameters-related Schemas.
# ==============================================================================
@dataclass
class DocumentPathParams:
    doc_id: int = Path(..., description="Document id")


# ==============================================================================
# Query parameters-related Schemas.
# ==============================================================================
@dataclass
class IncludeIndexQueryParams:
    include_index: bool = Query(
        False, description="Whether to return document indexing status or not"
    )
