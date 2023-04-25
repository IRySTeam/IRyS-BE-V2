from pydantic import BaseModel, Field
from typing import List, Optional

from app.search.enums.search import FilterOperatorEnum


class AdvancedFilterConditions(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")
    operator: FilterOperatorEnum = Field(..., description="Operator that will evaluate key and value relation")
    value: object = Field(..., description="Query to be evaluated")
    model: Optional[str] = Field(description="Bert client embedding model")
    scoring_algorithm: Optional[str] = Field(description="Scoring algorithm that Elasticsearch will perform")
    top_n: Optional[int] = Field(description="Result limit number")
    score_threshold: Optional[float] = Field(description="Result similarity cutoff score")
    data_type: str = Field(..., description="Denotes the data type of the entity")

class AdvancedSearchQuery(BaseModel):
    match: List[AdvancedFilterConditions] = Field(..., description="List of filter conditions that make up the advanced search query")
