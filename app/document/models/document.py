from sqlalchemy import Column, Unicode, BigInteger, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import TimestampMixin
from app.document.enums.document import IndexingStatusEnum


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    elastic_doc_id = Column(BigInteger, nullable=True)
    elastic_index_name = Column(Unicode(255), nullable=True)
    title = Column(Unicode(255), nullable=False)
    doc_created_at = Column(DateTime, nullable=True)
    doc_updated_at = Column(DateTime, nullable=True)
    
    index = relationship(
        "DocumentIndex",
        back_populates="doc", 
        uselist=False,
    )

class DocumentIndex(Base, TimestampMixin):
    __tablename__ = "document_indexes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_id = Column(BigInteger, ForeignKey("documents.id", ondelete="CASCADE"))
    status = Column(Enum(IndexingStatusEnum), nullable=False, default=IndexingStatusEnum.READY)
    reason = Column(Unicode(255), nullable=True)
    
    doc = relationship(
        "Document", 
        back_populates="index",
    )