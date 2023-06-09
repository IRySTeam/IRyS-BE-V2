from pydantic import BaseModel, Field


class MessageResponseSchema(BaseModel):
    message: str = Field(..., description="Message")
