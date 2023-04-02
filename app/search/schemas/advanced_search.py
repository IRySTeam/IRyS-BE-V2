from pydantic import BaseModel, Field
from typing import List

from app.search.enums import FilterOperator

class FilterConditions(BaseModel):
    key: str = Field(..., description="Entity name that will be evaluated")
    operator: FilterOperator = Field(..., description="Operator that will evaluate key and value relation")
    value: any = Field(..., description="Value that will be evaluated against key")

class AdvancedSearchQuery(BaseModel):
    match: List[FilterConditions] = Field(..., description="List of fitler conditions that make up the advanced search query")