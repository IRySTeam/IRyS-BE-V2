from typing import Literal, Optional

from pydantic import BaseModel, Field


class EditDocumentRequestSchema(BaseModel):
    title: Optional[str]
    is_public: Optional[bool]


class EditRepositoryDocumentRequestSchema(BaseModel):
    name: Optional[str] = Field(None, description="Document name")
    category: Optional[Literal["General", "Scientific", "Recruitment"]] = Field(
        None, description="Document category"
    )
    is_public: Optional[bool] = Field(None, description="Is public")


class AddDocumentCollaboratorRequestSchema(BaseModel):
    collaborator_id: int
    role: str


class EditDocumentCollaboratorRequestSchema(BaseModel):
    collaborator_id: int
    role: str


class RemoveDocumentCollaboratorRequestSchema(BaseModel):
    collaborator_id: int
