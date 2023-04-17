from typing import List, Optional
from pydantic import BaseModel, Field


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
    owner: RepositoryOwnerSchema = Field(..., description="Repository Owner")


class GetJoinedRepositoriesSchema(BaseModel):
    results: List[RepositorySchema] = Field(..., description="Results")
    total_page: int = Field(..., description="Total Page")
    total_items: int = Field(..., description="Total Items")


class GetPublicRepositoriesResponseSchema(BaseModel):
    results: List[RepositorySchema] = Field(..., description="Results")
    total_page: int = Field(..., description="Total Page")
    total_items: int = Field(..., description="Total Items")


class EditRepositoryResponseSchema(BaseModel):
    message: str = Field(..., description="Message")
