from typing import Optional
from pydantic import BaseModel, Field


class CreateRepositoryRequestSchema(BaseModel):
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")
    is_public: bool = Field(..., description="Is Public")


class EditRepositoryRequestSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_public: Optional[str]
