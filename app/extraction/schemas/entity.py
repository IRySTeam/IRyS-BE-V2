from typing import Any, Mapping
from pydantic import BaseModel, Field

class DomainEntityResponse(BaseModel):
    name: str = Field(..., description="Name of the entity")
    type: str = Field(..., description="Type of the entity")
    operators: list[str] = Field(..., description="List of supported operators for the entity")