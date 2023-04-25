from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Unicode
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import mapped_column, relationship

from app.document.enums.document import IndexingStatusEnum
from core.db import Base
from core.db.mixins import TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Unicode(255), nullable=False)
    file_url = Column(Unicode(255), nullable=False)
    elastic_doc_id = Column(Unicode(255), nullable=True)
    elastic_index_name = Column(Unicode(255), nullable=True)
    repository_id = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    repository = relationship("Repository", back_populates="documents")
    title = Column(Unicode(255), nullable=False)
    doc_created_at = Column(DateTime, nullable=True)
    doc_updated_at = Column(DateTime, nullable=True)
    file_content_str = Column(TEXT, nullable=True)

    index = relationship(
        "DocumentIndex",
        back_populates="doc",
        uselist=False,
    )
    repository_id = Column(BigInteger, ForeignKey("repositories.id"))
    repository = relationship("Repository", back_populates="documents")


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
