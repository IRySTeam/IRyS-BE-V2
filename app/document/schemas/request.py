from typing import Optional

from pydantic import BaseModel


class EditDocumentRequestSchema(BaseModel):
    title: Optional[str]
    is_public: Optional[bool]


class AddDocumentCollaboratorRequestSchema(BaseModel):
    collaborator_id: int
    role: str


class EditDocumentCollaboratorRequestSchema(BaseModel):
    collaborator_id: int
    role: str


class RemoveDocumentCollaboratorRequestSchema(BaseModel):
    collaborator_id: int
