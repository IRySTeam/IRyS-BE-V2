from dataclasses import dataclass
from pydantic import BaseModel, Field
from fastapi import Path

# ==============================================================================
# Request Body-related Schemas.
# ==============================================================================


# ==============================================================================
# Response Body-related Schemas.
# ==============================================================================
class DomainMetadataResponse(BaseModel):
    name: str = Field(..., description="Name of the metadata")
    type: str = Field(..., description="Type of the metadata")
    operators: list[str] = Field(
        ..., description="List of supported operators for the metadata"
    )


# ==============================================================================
# Path parameters-related Schemas.
# ==============================================================================
@dataclass
class DomainMetadataPathParams:
    domain: str = Path(..., description="Domain name")


# ==============================================================================
# Query parameters-related Schemas.
# ==============================================================================
