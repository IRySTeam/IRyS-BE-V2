from typing import List

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Table,
    Unicode,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.db.mixins import TimestampMixin

user_repositories = Table(
    "user_repositories",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column(
        "repository_id", BigInteger, ForeignKey("repositories.id"), primary_key=True
    ),
    Column("role", Unicode(255), nullable=False),
)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(Unicode(255), nullable=False)
    last_name = Column(Unicode(255))
    email = Column(Unicode(255), nullable=False)
    password = Column(Unicode(255), nullable=False)
    last_login = Column(DateTime, default=func.now(), nullable=False)
    refresh_token = Column(Unicode(255))
    refresh_token_valid_until = Column(DateTime)
    otp = Column(Unicode(255))
    otp_valid_until = Column(DateTime)
    forgot_password_otp = Column(Unicode(255))
    forgot_password_otp_valid_until = Column(DateTime)
    repositories: Mapped[List["Repository"]] = relationship(
        "Repository", secondary=user_repositories, back_populates="users"
    )
