from core.db import Transactional
from core.repository import FaqRepo


class FaqService:
    faq_repo = FaqRepo()

    @Transactional()
    async def create_question(self, question: str):
        saved_question = await self.faq_repo.save({"question": question})
        return saved_question.inserted_primary_key[0]
