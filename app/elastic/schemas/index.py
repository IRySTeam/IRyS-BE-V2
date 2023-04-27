from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional

from fastapi import Path, Query
from pydantic import BaseModel, Field

from app.elastic.configuration import (
    GENERAL_ELASTICSEARCH_INDEX_MAPPINGS,
    GENERAL_ELASTICSEARCH_INDEX_SETTINGS,
)

# ==============================================================================
# Request Body-related Schemas.
# ==============================================================================


class IndexType(str, Enum):
    NONE = "none"
    GENERAL = "general"
    RECRUITMENT = "recruitment"
    SCIENTIFIC = "scientific"


class CreateIndexBody(BaseModel):
    index_name: str = Field(..., description="Name of the index")
    index_type: IndexType = Field(
        IndexType.GENERAL,
        description="Type of the index, available values are none, general, recruitment, and "
        "scientific, if none is selected, the index will be created with the given mappings and "
        "settings, otherwise, the index will be created with the corresponding settings and "
        "mappings defined by the application",
    )
    mappings: Optional[Mapping[str, Any]] = Field(
        GENERAL_ELASTICSEARCH_INDEX_MAPPINGS,
        description="Define how a document, and the fields it contains, are stored and indexed. "
        "For more information, refer to "
        "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/mapping.html)",
    )
    settings: Optional[Mapping[str, Any]] = Field(
        GENERAL_ELASTICSEARCH_INDEX_SETTINGS,
        description="Index configuration, there are static (unchangeable) and dynamic (changeable) "
        "settings. For more information, refer to "
        "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/index-modules.html#index-modules-settings)",
    )

    class Config:
        use_enum_values = True


class UpdateIndexBody(BaseModel):
    settings: Mapping[str, Any] = Field(
        ...,
        description="Index configuration that are changeable. For more information, refer to "
        "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/index-modules.html#index-modules-settings)",
    )


# ==============================================================================
# Response Body-related Schemas.
# ==============================================================================
# Elasticsearch index information returned by the Elasticsearch cat API (client.cat.indices()
# method)
class ElasticIndexCat(BaseModel):
    health: str = Field(
        ...,
        description="Health of the index, available values are green, yellow and red",
    )
    status: str = Field(
        ...,
        description="Status of the index, available values are open, close, and hidden",
    )
    index: str = Field(..., description="Name of the index")
    uuid: str = Field(..., description="Unique identifier for the index")
    pri: int = Field(..., description="Number of primary shards")
    rep: int = Field(..., description="Number of replica shards")
    docs_count: int = Field(..., description="Number of documents", alias="docs.count")
    docs_deleted: int = Field(
        ..., description="Number of deleted documents", alias="docs.deleted"
    )
    store_size: str = Field(..., description="Size of the index", alias="store.size")
    primary_store_size: str = Field(
        ..., description="Size of the primary shards", alias="pri.store.size"
    )


class ElasticIndexDetail(BaseModel):
    aliases: Mapping[str, Any] = Field(..., description="Aliases for the index")
    mappings: Mapping[str, Any] = Field(
        ...,
        description="Define how a document, and the fields it contains, are stored and indexed."
        " For more information, refer to "
        "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/mapping.html)",
    )
    settings: Mapping[str, Any] = Field(
        ...,
        description="Index configuration, there are static (unchangeable) and dynamic (changeable)"
        " settings. For more information, refer to "
        "[this](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/index-modules.html#index-modules-settings)",
    )


class ElasticIndexUpdateResponse(BaseModel):
    updated: bool = Field(..., description="Whether the index was updated or not")


class ElasticIndexDeleteResponse(BaseModel):
    deleted: bool = Field(..., description="Whether the index was deleted or not")


class ElasticCreateIndexResponse(BaseModel):
    acknowledged: bool = Field(
        ..., description="Whether the request was acknowledged or not"
    )
    shards_acknowledged: bool = Field(
        ..., description="Whether the request was acknowledged by all shards or not"
    )
    index: str = Field(..., description="Name of the index")


# ==============================================================================
# Path parameters-related Schemas.
# ==============================================================================
@dataclass
class IndexNamePathParams:
    index_name: str = Path(..., description="Name of the index")


# ==============================================================================
# Query parameters-related Schemas.
# ==============================================================================
@dataclass
class GetAllIndexQueryParams:
    all: bool = Query(
        False, description="Whether to return auto-generated indices or not"
    )
