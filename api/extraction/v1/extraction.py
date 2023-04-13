from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.exception import BaseHttpErrorSchema
from app.extraction import TYPE_OPERATORS, METADATA
from app.extraction.schemas import (
    DomainMetadataResponse,
    DomainMetadataPathParams,
)

extraction_router = APIRouter()


@extraction_router.get(
    "/domains",
    response_model=List[str],
    description="Get all domains",
)
async def get_domains():
    return list(METADATA.keys())


@extraction_router.get(
    "/metadata/{domain}",
    response_model=List[DomainMetadataResponse],
    description="Get metadata list of a domain",
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        },
    },
)
async def get_entities(path: DomainMetadataPathParams = Depends()):
    if path.domain not in METADATA:
        raise HTTPException(
            status_code=400,
            detail="Domain does not exist",
        )
    entities = METADATA[path.domain]
    for entity in entities:
        entity["operators"] = TYPE_OPERATORS[entity["type"]]
    return entities
