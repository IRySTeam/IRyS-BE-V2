from sqlalchemy import Column, Unicode, BigInteger, DateTime, func

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
    refresh_token = Column(Unicode(255))
    refresh_token_valid_until = Column(DateTime)
    otp = Column(Unicode(255))
    otp_valid_until = Column(DateTime)
    forgot_password_otp = Column(Unicode(255))
    forgot_password_otp_valid_until = Column(DateTime)
