from sqlalchemy import BigInteger, Column, Unicode

from core.db import Base
from core.db.mixins import TimestampMixin


class Faq(Base, TimestampMixin):
    __tablename__ = "faq"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question = Column(Unicode(255), nullable=False)
