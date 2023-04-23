from pydantic import BaseModel, Field
from typing import List, Optional

from app.search.enums.search import (
    # SearchAlgorithmEnum, 
    ScoringAlgorithmEnum, 
    DomainEnum
)
from app.search.schemas.elastic import MatchedDocument
from app.search.schemas.advanced_search import AdvancedSearchQuery

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Raw user query input")
    advanced_filter: AdvancedSearchQuery = Field(..., description="Additional entity based filters")

class SemanticSearchRequestDepr(BaseModel):
    query: str = Field(..., description="Raw user query input")
    # algorithm: SearchAlgorithmEnum = Field(..., description="The type of searching method that will be performed")
    domain: DomainEnum = Field(..., description="Document domain of the search")
    scoring: ScoringAlgorithmEnum = Field(..., description="The scoring algorithm that will be used to evaluate the query and the indexed documents")
    advanced_filter: AdvancedSearchQuery = Field(..., description="Additional entity based filters")

class SemanticSearchResponseSchema(BaseModel):
    message: str = Field(..., description="Response message")
    document_list: List[MatchedDocument] = Field(..., description="List of matched documents")

    