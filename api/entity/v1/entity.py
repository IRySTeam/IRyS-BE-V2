from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.exception import BaseHttpErrorSchema
from app.extraction.entities.config import DOMAIN_ENTITIES, TYPE_OPERATORS
from app.extraction.schemas.entity import DomainEntityResponse
from api.entity.v1.request import DomainEntitiesPathParams

entity_router = APIRouter()

@entity_router.get(
    "/domains",
    response_model=List[str],
    description="Get all domains",
)
async def get_domains():
    return list(DOMAIN_ENTITIES.keys())


@entity_router.get(
    "/{domain}",
    response_model=List[DomainEntityResponse],
    description="Get all entities of a domain",
    responses = {
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query"
        },
    }
)
async def get_entities(path: DomainEntitiesPathParams = Depends()):
    if path.domain not in DOMAIN_ENTITIES:
        raise HTTPException(
            status_code=400,
            detail="Domain does not exist",
        )
    entities = DOMAIN_ENTITIES[path.domain]
    for entity in entities:
        entity["operators"] = TYPE_OPERATORS[entity["type"]]
    return entities
