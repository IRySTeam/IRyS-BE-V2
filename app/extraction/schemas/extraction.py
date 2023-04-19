from dataclasses import dataclass
from pydantic import BaseModel, Field
from fastapi import Path
from typing import List

# ==============================================================================
# Request Body-related Schemas.
# ==============================================================================


# ==============================================================================
# Response Body-related Schemas.
# ==============================================================================
class DomainInformationResponse(BaseModel):
    name: str = Field(..., description="Name of the information")
    type: str = Field(..., description="Type of the information")
    operators: List[str] = Field(
        ..., description="List of supported operators for the information"
    )


class DomainEntitiesResponse(BaseModel):
    name: str = Field(..., description="Name of the entities")
    type: str = Field(..., description="Type of the entities")
    operators: List[str] = Field(
        ..., description="List of supported operators for the entities"
    )


class ExtractedInformationResponse(BaseModel):
    entities: List[DomainEntitiesResponse] = Field(..., description="List of entities")
    information: List[DomainInformationResponse] = Field(
        ..., description="List of domain specific information"
    )


# ==============================================================================
# Path parameters-related Schemas.
# ==============================================================================
@dataclass
class ExtractedInformationPathParams:
    domain: str = Path(..., description="Domain name")


# ==============================================================================
# Query parameters-related Schemas.
# ==============================================================================
