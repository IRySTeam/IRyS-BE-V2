from pydantic import BaseModel, Field

class BaseHttpErrorSchema(BaseModel):
    detail: str = Field(..., description="Error message")
    