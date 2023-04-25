from typing import List

from sqlalchemy import BigInteger, Boolean, Column, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.user.models import user_repositories
from core.db import Base
from core.db.mixins import TimestampMixin


class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255))
    documents: Mapped[List["Document"]] = relationship(back_populates="repository")
    is_public = Column(Boolean, default=True)
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_repositories, back_populates="repositories"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="repository"
    )
