from pydantic import BaseModel, Field

from app.document.enums.document import IndexingStatusEnum


class DocumentIndexSchema(BaseModel):
    id: int = Field(..., description="Document indexing id")
    doc_id: int = Field(..., description="Corresponding document id")
    status: IndexingStatusEnum = Field(..., description="Indexing status")
    reason: str = Field(None, description="Reason for failure / success message")

    class Config:
        orm_mode = True


class DocumentSchema(BaseModel):
    id: int = Field(..., description="Document id")
    title: str = Field(..., description="Document title")
    file_url: str = Field(..., description="Document file url")
    elastic_doc_id: int = Field(None, description="Document id in Elasticsearch")
    elastic_index_name: str = Field(None, description="Elasticsearch index name")
    index: DocumentIndexSchema = Field(None, description="Document indexing status")

    class Config:
        orm_mode = True


class DocumentCollaboratorSchema(BaseModel):
    id: int = Field(..., description="User id")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email")
    role: str = Field(..., description="Role")

    class Config:
        orm_mode = True
