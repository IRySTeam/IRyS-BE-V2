from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: int = Field(None, description="ID")
    is_email_verified: bool = Field(None, description="Has email been verified")

    class Config:
        validate_assignment = True
