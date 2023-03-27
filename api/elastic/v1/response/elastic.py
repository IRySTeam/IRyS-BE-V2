from pydantic import BaseModel, Field

class ElasticIndexUpdateResponse(BaseModel):
    updated: bool = Field(..., description="Whether the index was updated or not")
    
class ElasticIndexDeleteResponse(BaseModel):
    deleted: bool = Field(..., description="Whether the index was deleted or not")