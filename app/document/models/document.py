from typing import List

from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, Unicode
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.document.enums.document import IndexingStatusEnum
from app.user.models import user_documents
from core.db import Base
from core.db.mixins import TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Unicode(255), nullable=False)
    file_url = Column(Unicode(255), nullable=False)
    title = Column(Unicode(255), nullable=False)
    general_elastic_doc_id = Column(Unicode(255), nullable=True)
    elastic_doc_id = Column(Unicode(255), nullable=True)
    elastic_index_name = Column(Unicode(255), nullable=True)
    file_content_str = Column(TEXT, nullable=True)
    is_public = Column(Boolean, default=True)
    repository_id = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    repository = relationship("Repository", back_populates="documents")
    mimetype = Column(Unicode(255), nullable=True)
    extension = Column(Unicode(255), nullable=True)
    size = Column(BigInteger, nullable=True)
    file_content_str = Column(TEXT, nullable=True)
    collaborators: Mapped[List["User"]] = relationship(
        "User", secondary=user_documents, back_populates="documents"
    )

    index = relationship(
        "DocumentIndex",
        back_populates="doc",
        uselist=False,
    )


class DocumentIndex(Base, TimestampMixin):
    __tablename__ = "document_indexes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_id = Column(BigInteger, ForeignKey("documents.id", ondelete="CASCADE"))
    status = Column(
        Enum(IndexingStatusEnum), nullable=False, default=IndexingStatusEnum.READY
    )
    reason = Column(TEXT, nullable=True)
    current_task_id = Column(Unicode(255), nullable=True)

    doc = relationship(
        "Document",
        back_populates="index",
    )
