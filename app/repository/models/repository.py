from typing import List

from sqlalchemy import Column, Unicode, BigInteger, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.user.models import user_repositories
from core.db import Base
from core.db.mixins import TimestampMixin


class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255))
    is_public = Column(Boolean, default=True)
    users: Mapped[List["User"]]  = relationship(
        secondary=user_repositories, back_populates="repositories"
    )