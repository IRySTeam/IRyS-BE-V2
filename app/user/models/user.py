from sqlalchemy import Column, Unicode, BigInteger, Boolean, DateTime, func

from core.db import Base
from core.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(Unicode(255), nullable=False)
    last_name = Column(Unicode(255))
    email = Column(Unicode(255), nullable=False)
    password = Column(Unicode(255), nullable=False)
    last_login = Column(DateTime, default=func.now(), nullable=False)
