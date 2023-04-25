from typing import List

from pydantic import BaseModel, Field


class MatchedDocument(BaseModel):
    id: str = Field(..., description="UUID of the matched document")
    score: float = Field(..., description="Numeric score the matched document was given by the scoring algorithm based on the search query")
    title: str = Field(..., description="The title of the document")
    document_metadata: dict[str, str] = Field(..., description="Key value pair mappings of recognized extracted entities")
    
class SearchResult(BaseModel):
    result: List[MatchedDocument] = Field(..., description="Collection of matched documents from ElasticSearch")

class MatchedDocumentDepr(BaseModel):
    id: str = Field(..., description="UUID of the matched document")
    url: str = Field(
        ...,
        description="Url leading to the path of the matched document in S3 object storage",
    )
    rank: int = Field(
        ...,
        description="Final ranking of matched document based on search query for result ordering",
    )
    score: float = Field(
        ...,
        description="Numeric score the matched document was given by the scoring algorithm based on the search query",
    )
