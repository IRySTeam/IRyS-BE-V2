from typing import Any, Mapping
from pydantic import BaseModel, Field

class CreateIndexBody(BaseModel):
  index_name: str = Field(..., description="Name of the index")
  mappings: Mapping[str, Any] = Field(
    None, 
    description="Define how a document, and the fields it contains, are stored and indexed. "\
      "For more information, refer to "\
      "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/mapping.html)"
  )
  settings: Mapping[str, Any] = Field(
    None, 
    description="Index configuration, there are static (unchangeable) and dynamic (changeable) "\
      "settings. For more information, refer to "\
      "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/index-modules.html#index-modules-settings)" \
  )

class UpdateIndexBody(BaseModel):
  settings: Mapping[str, Any] = Field(
    ..., 
    description="Index configuration that are changeable. For more information, refer to "\
      "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/index-modules.html#index-modules-settings)" \
  )