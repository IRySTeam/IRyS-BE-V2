from pydantic import BaseModel, Field
from typing import List, TypedDict

class ElasticSearchDocumentItem(BaseModel):
    query: str = Field(..., description="The query that was evaluated against the document to produce relevance score")
    ner_entity: List[str] = Field(..., description="Key value pair mappings of recognized NER extracted entities")
    metadata_entity: List[str] = Field(..., description="Key value pair mappings of recognized document metadata entities")
    score: float = Field(..., description="Numeric score the matched document was given by the scoring algorithm based on the search query")

class ElasticSearchResult(BaseModel):
    result: List[ElasticSearchDocumentItem] = Field(..., description="Collection of matched documents from ElasticSearch")

class MatchedDocument(BaseModel):
    id: str = Field(..., description="UUID of the matched document")
    url: str = Field(..., description="Url leading to the path of the matched document in S3 object storage")
    rank: int = Field(..., description="Final ranking of matched document based on search query for result ordering")
    score: float = Field(..., description="Numeric score the matched document was given by the scoring algorithm based on the search query")
