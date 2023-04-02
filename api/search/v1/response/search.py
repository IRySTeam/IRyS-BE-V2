from pydantic import BaseModel, Field
from typing import List

from app.search.schemas import MatchedDocument

class SemanticSearchResponseSchema(BaseModel):
    message: str = Field(..., description="Response message")
    document_list: List[MatchedDocument] = Field(..., description="List of matched documents")