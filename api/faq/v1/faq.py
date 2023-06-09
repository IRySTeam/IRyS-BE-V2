from fastapi import APIRouter

from app.faq.schemas import CreateQuestionRequestSchema, MessageResponseSchema
from app.faq.services import FaqService

faq_router = APIRouter()


@faq_router.post(
    "/create",
    description="Create a question",
    responses={},
)
async def create_question(body: CreateQuestionRequestSchema):
    await FaqService().create_question(body.question)
    return MessageResponseSchema(message="Question created successfully")
