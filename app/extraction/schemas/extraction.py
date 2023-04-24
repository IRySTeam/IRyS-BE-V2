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
class ExtractedInformationResponse(BaseModel):
    name: str = Field(..., description="Name of the information")
    type: str = Field(..., description="Type of the information")
    operators: List[str] = Field(
        ..., description="List of supported operators for the information"
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
