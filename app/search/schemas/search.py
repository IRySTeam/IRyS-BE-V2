from typing import List

from pydantic import BaseModel, Field

from app.document.schemas.document import DocumentResponseSchema
from app.search.enums.search import DomainEnum  # SearchAlgorithmEnum,
from app.search.schemas.advanced_search import AdvancedSearchQuery


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Raw user query input")
    domain: DomainEnum = Field(..., description="Document domain of the search")
    # algorithm: SearchAlgorithmEnum = Field(..., description="The type of searching method that will be performed") TO DO: Atau ini ganti model
    # scoring: ScoringAlgorithmEnum = Field(..., description="The scoring algorithm that will be used to evaluate the query and the indexed documents")
    advanced_filter: AdvancedSearchQuery = Field(
        ..., description="Additional entity based filters"
    )

class DocumentDetails(BaseModel):
    details: DocumentResponseSchema = Field(
        ..., description="Document details from database"
    )
    preview: str = Field(..., description="Text snippet for preview")
    highlights: List[str] = Field(
        ..., description="List of texts that will be highlighted in preview"
    )

class SemanticSearchResponseSchema(BaseModel):
    num_docs_retrieved: int = Field(..., description="Number of matched documents")
    result: List[DocumentDetails] = Field(..., description="List of matched documents")

class RepoSearchPathParams(BaseModel):
    repository_id: int = Field(..., description="Unique identifier of current repository")

class FileSearchPathParams(BaseModel):
    domain: DomainEnum = Field(..., description="Document domain of the search")
    repository_id: int = Field(..., description="Unique identifier of current repository")
