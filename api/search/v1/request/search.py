from pydantic import BaseModel, Field

from app.search.schemas import AdvancedSearchQuery
from app.search.enums import SearchAlgorithmEnum, ScoringAlgorithmEnum, DomainEnum

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Raw user query input")
    algorithm: SearchAlgorithmEnum = Field(..., description="The type of searching method that will be performed")
    domain: DomainEnum = Field(..., description="Document domain of the search")
    scoring: ScoringAlgorithmEnum = Field(..., description="The scoring algorithm that will be used to evaluate the query and the indexed documents")
    advanced_filter: AdvancedSearchQuery = Field(..., description="Additional entity based filters")