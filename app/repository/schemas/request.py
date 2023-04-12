from pydantic import BaseModel, Field

class CreateRepositoryRequestSchema(BaseModel):
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")
    is_public: bool = Field(..., description="Is Public")