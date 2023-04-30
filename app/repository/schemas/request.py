from dataclasses import dataclass
from enum import Enum
from typing import Optional

from fastapi import Path, Query
from pydantic import BaseModel, Field


class IndexingStatus(str, Enum):
    ALL = "ALL"
    READY = "READY"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    INDEXING = "INDEXING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class CreateRepositoryRequestSchema(BaseModel):
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")
    is_public: bool = Field(..., description="Is Public")


class EditRepositoryRequestSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_public: Optional[bool]


class AddRepositoryCollaboratorRequestSchema(BaseModel):
    collaborator_id: int = Field(..., description="User ID")
    role: str = Field(..., description="Role")


class EditRepositoryCollaboratorRequestSchema(BaseModel):
    collaborator_id: int = Field(..., description="User ID")
    role: str = Field(..., description="Role")


class RemoveRepositoryCollaboratorRequestSchema(BaseModel):
    collaborator_id: int = Field(..., description="User ID")


@dataclass
class MonitorAllDocumentPathParams:
    repository_id: int = Path(..., description="Repository id")


@dataclass
class ReindexDocumentPathParams:
    doc_id: int = Path(..., description="Document id")


@dataclass
class ReindexAllDocumentPathParams:
    repository_id: int = Path(..., description="Repository id")


@dataclass
class MonitorAllDocumentQueryParams:
    status: IndexingStatus = Query(..., description="Type")
    page_no: int = Query(1, description="Page Number")
    page_size: int = Query(10, description="Page Size")
