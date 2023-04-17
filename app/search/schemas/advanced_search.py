from pydantic import BaseModel, Field
from typing import List

from app.search.enums.search import FilterOperatorEnum

class BasicFilterConditions(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")
    operator: FilterOperatorEnum = Field(..., description="Operator that will evaluate key and value relation")
    value: object = Field(..., description="Query to be evaluated")

class SemanticFilterConditions(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")
    model: str = Field(..., description="Bert client embedding model")
    scoring_algorithm: str = Field(..., description="Scoring algorithm that Elasticsearch will perform")
    top_n: float = Field(..., description="Result limit number")
    score_threshold: float = Field(..., description="Result similarity cutoff score")
    value: object = Field(..., description="Query to be evaluated")

class FilterConditionsDepr(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")
    operator: FilterOperatorEnum = Field(..., description="Operator that will evaluate key and value relation")

class AdvancedSearchQuery(BaseModel):
    basic_match: List[BasicFilterConditions] = Field(..., description="List of basic filter conditions that make up the advanced search query")
    semantic_match: List[SemanticFilterConditions] = Field(..., description="List of semantic filter conditions that make up the advanced search query")