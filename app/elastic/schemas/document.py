from pydantic import BaseModel, Field

# ==============================================================================
# Request Body-related Schemas.
# ==============================================================================


# ==============================================================================
# Response Body-related Schemas.
# ==============================================================================
class ShardInformation(BaseModel):
	total: int = Field(..., description="Total number of shards")
	successful: int = Field(..., description="Number of successful shards")
	failed: int = Field(..., description="Number of failed shards")
 
class ElasticDocumentIndexedResponse(BaseModel):
  index: str = Field(..., description="Name of the index", alias="_index")
  id: str = Field(..., description="Unique identifier for the document", alias="_id")
  version: int = Field(..., description="Version of the document", alias="_version")
  result: str = Field(..., description="Result of the operation")
  shards: ShardInformation = Field(..., description="Shard information", alias="_shards")
  seq_no: int = Field(..., description="Sequence number", alias="_seq_no")
  primary_term: int = Field(..., description="Primary term", alias="_primary_term")
  
# ==============================================================================
# Path parameters-related Schemas.
# ==============================================================================


# ==============================================================================
# Query parameters-related Schemas.
# ==============================================================================
 