from pydantic import BaseModel, Field


class CreateQuestionRequestSchema(BaseModel):
    question: str = Field(..., description="Question")
