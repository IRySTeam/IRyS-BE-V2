from pydantic import BaseModel, Field
from typing import List

from app.search.enums.search import FilterOperatorEnum

class FilterConditions(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")

class FilterConditionsDepr(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")
    operator: FilterOperatorEnum = Field(..., description="Operator that will evaluate key and value relation")

class AdvancedSearchQuery(BaseModel):
    match: List[FilterConditions] = Field(..., description="List of fitler conditions that make up the advanced search query")