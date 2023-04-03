from typing import Any, Mapping
from pydantic import BaseModel, Field

# Elasticsearch index information returned by the Elasticsearch cat API (client.cat.indices() 
# method)
class ElasticIndexCat(BaseModel):
  health: str = Field(
   ..., 
   description="Health of the index, available values are green, yellow and red"
  )
  status: str = Field(
   ...,
   description="Status of the index, available values are open, close, and hidden"
  )
  index: str = Field(..., description="Name of the index")
  uuid: str = Field(..., description="Unique identifier for the index")
  pri: int = Field(..., description="Number of primary shards")
  rep: int = Field(..., description="Number of replica shards")
  docs_count: int = Field(..., description="Number of documents", alias="docs.count")
  docs_deleted: int = Field(..., description="Number of deleted documents", alias="docs.deleted")
  store_size: str = Field(..., description="Size of the index", alias="store.size")
  primary_store_size: str = Field(
    ..., 
    description="Size of the primary shards", 
    alias="pri.store.size"
  )

class ElasticIndexDetail(BaseModel):
  aliases: Mapping[str, Any] = Field(..., description="Aliases for the index")
  mappings: Mapping[str, Any] = Field(
    ..., 
    description="Define how a document, and the fields it contains, are stored and indexed."\
      " For more information, refer to "\
      "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/mapping.html)"
  )
  settings: Mapping[str, Any] = Field(
    ..., 
    description="Index configuration, there are static (unchangeable) and dynamic (changeable)"\
      " settings. For more information, refer to "\
      "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/index-modules.html#index-modules-settings)" \
  )
  
class ElasticCreateIndexResponse(BaseModel):
  acknowledged: bool = Field(..., description="Whether the request was acknowledged or not")
  shards_acknowledged: bool = Field(
    ..., 
    description="Whether the request was acknowledged by all shards or not"
  )
  index: str = Field(..., description="Name of the index")