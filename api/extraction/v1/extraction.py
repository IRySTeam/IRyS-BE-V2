from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.exception import BaseHttpErrorSchema
from app.extraction import EXTRACTED_INFORMATION, TYPE_OPERATORS
from app.extraction.schemas import (
    ExtractedInformationPathParams,
    ExtractedInformationResponse,
)

extraction_router = APIRouter()


@extraction_router.get(
    "/domains",
    response_model=List[str],
    description="Get all domains",
)
async def get_domains():
    return list(EXTRACTED_INFORMATION.keys())


@extraction_router.get(
    "/information/{domain}",
    response_model=List[ExtractedInformationResponse],
    description="Get extracted information list of a domain",
    responses={
        400: {
            "model": BaseHttpErrorSchema,
            "description": "Bad request, please check request body, params, headers, or query",
        },
    },
)
async def get_information(path: ExtractedInformationPathParams = Depends()):
    if path.domain not in EXTRACTED_INFORMATION:
        raise HTTPException(
            status_code=400,
            detail="Domain does not exist",
        )
    information = EXTRACTED_INFORMATION[path.domain]
    for info in information:
        info["operators"] = TYPE_OPERATORS[info["type"]]

    return information
