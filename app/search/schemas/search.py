from pydantic import BaseModel, Field
from typing import List, Optional

from app.search.enums.search import (
    # SearchAlgorithmEnum, 
    ScoringAlgorithmEnum, 
    DomainEnum
)
from app.search.schemas.elastic import MatchedDocument
from app.search.schemas.advanced_search import AdvancedSearchQuery
from app.document.schemas.document import DocumentResponseSchema

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Raw user query input")
    domain: DomainEnum = Field(..., description="Document domain of the search")
    # algorithm: SearchAlgorithmEnum = Field(..., description="The type of searching method that will be performed") TO DO: Atau ini ganti model
    # scoring: ScoringAlgorithmEnum = Field(..., description="The scoring algorithm that will be used to evaluate the query and the indexed documents")
    advanced_filter: AdvancedSearchQuery = Field(..., description="Additional entity based filters")

class DocumentDetails(BaseModel):
    details: DocumentResponseSchema = Field(..., description="Document details from database")
    preview: str = Field(..., description="Text snippet for preview")
    highlights: List[str] = Field(..., description="List of texts that will be highlighted in preview")

class SemanticSearchResponseSchema(BaseModel):
    message: str = Field(..., description="Response message")
    result: List[DocumentDetails] = Field(..., description="List of matched documents")


