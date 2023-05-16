from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.document.schemas import (
    DocumentDatabaseResponseSchema,
    MonitorDocumentResponseSchema,
)


class MessageResponseSchema(BaseModel):
    message: str = Field(..., description="Message")


class CountResponseSchema(BaseModel):
    count: int = Field(..., description="The number of data")


class CreateRepositoryResponseSchema(BaseModel):
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")
    is_public: bool = Field(..., description="Is Public")

    class Config:
        orm_mode = True


class RepositoryOwnerSchema(BaseModel):
    id: int = Field(..., description="User ID")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")

    class Config:
        orm_mode = True


class RepositorySchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")
    is_public: bool = Field(..., description="Is Public")
    updated_at: datetime = Field(..., description="Updated At")
    owner: RepositoryOwnerSchema = Field(..., description="Repository Owner")


class RepositoryDetailsResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")
    is_public: bool = Field(..., description="Is Public")
    updated_at: datetime = Field(..., description="Updated At")
    owner: RepositoryOwnerSchema = Field(..., description="Repository Owner")
    current_user_role: Optional[str] = Field(None, description="Current User Role")


class GetJoinedRepositoriesSchema(BaseModel):
    does_user_have_any_repos: bool = Field(..., description="Does User Have Any Repos")
    results: List[RepositorySchema] = Field(..., description="Results")
    total_page: int = Field(..., description="Total Page")
    total_items: int = Field(..., description="Total Items")


class GetPublicRepositoriesResponseSchema(BaseModel):
    results: List[RepositorySchema] = Field(..., description="Results")
    total_page: int = Field(..., description="Total Page")
    total_items: int = Field(..., description="Total Items")


class EditRepositoryResponseSchema(BaseModel):
    message: str = Field(..., description="Message")


class RepositoryCollaboratorSchema(BaseModel):
    id: int = Field(..., description="User ID")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    email: str = Field(..., description="Email")
    role: str = Field(..., description="Role")

    class Config:
        orm_mode = True


class MonitorAllDocumentResponseSchema(BaseModel):
    results: List[MonitorDocumentResponseSchema] = Field(..., description="Results")
    current_page: int = Field(..., description="Current Page")
    total_pages: int = Field(..., description="Total Page")
    total_items: int = Field(..., description="Total Items")


class AllDocumentDatabaseResponseSchema(BaseModel):
    results: List[DocumentDatabaseResponseSchema] = Field(..., description="Results")
    current_page: int = Field(..., description="Current Page")
    total_pages: int = Field(..., description="Total Page")
    total_items: int = Field(..., description="Total Items")
