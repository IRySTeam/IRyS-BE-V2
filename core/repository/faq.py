from app.faq.models import Faq
from core.repository import BaseRepo


class FaqRepo(BaseRepo[Faq]):
    def __init__(self):
        super().__init__(Repository)
