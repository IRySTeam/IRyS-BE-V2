from typing import List

from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, Unicode
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.document.enums.document import IndexingStatusEnum
from app.elastic import EsClient
from app.elastic.configuration import (
    GENERAL_ELASTICSEARCH_INDEX_NAME,
    SCIENTIFIC_ELASTICSEARCH_INDEX_NAME,
)
from app.extraction.configuration import (
    GENERAL_ENTITIES,
    GENERAL_INFORMATION_NOT_FLATTENED,
    RECRUITMENT_ENTITIES,
    RECRUITMENT_INFORMATION_NOT_FLATTENED,
    SCIENTIFIC_ENTITIES,
    SCIENTIFIC_INFORMATION_NOT_FLATTENED,
)
from app.user.models import user_documents
from core.db import Base
from core.db.mixins import TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Unicode(255), nullable=False)
    file_url = Column(Unicode(255), nullable=False)
    general_elastic_doc_id = Column(Unicode(255), nullable=True)
    elastic_doc_id = Column(Unicode(255), nullable=True)
    elastic_index_name = Column(Unicode(255), nullable=True)
    is_public = Column(Boolean, default=True)
    repository_id = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    repository = relationship("Repository", back_populates="documents")
    mimetype = Column(Unicode(255), nullable=True)
    extension = Column(Unicode(255), nullable=True)
    size = Column(BigInteger, nullable=True)
    uploaded_by = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    uploader = relationship("User", back_populates="uploaded_documents")
    collaborators: Mapped[List["User"]] = relationship(
        "User", secondary=user_documents, back_populates="documents"
    )

    index = relationship(
        "DocumentIndex",
        back_populates="doc",
        uselist=False,
    )

    @hybrid_property
    def category(self):
        category = "Determining...."
        if self.general_elastic_doc_id:
            category = "General"
            if self.elastic_doc_id and self.elastic_index_name:
                category = (
                    "Scientific"
                    if self.elastic_index_name == SCIENTIFIC_ELASTICSEARCH_INDEX_NAME
                    else "Recruitment"
                )

        return category

    @hybrid_property
    def doc_detail(self):
        doc_entity = {}
        doc_metadata = {}

        metadata_iterator: dict = None
        entity_iterator: dict = None
        elastic_document: dict = None
        if self.elastic_index_name and self.elastic_doc_id:
            metadata_iterator = (
                SCIENTIFIC_INFORMATION_NOT_FLATTENED
                if self.elastic_index_name == SCIENTIFIC_ELASTICSEARCH_INDEX_NAME
                else RECRUITMENT_INFORMATION_NOT_FLATTENED
            )
            metadata_iterator += GENERAL_INFORMATION_NOT_FLATTENED
            entity_iterator = (
                SCIENTIFIC_ENTITIES
                if self.elastic_index_name == SCIENTIFIC_ELASTICSEARCH_INDEX_NAME
                else RECRUITMENT_ENTITIES
            )
            elastic_document = EsClient.get_doc(
                index=self.elastic_index_name, doc_id=self.elastic_doc_id
            )
        elif self.general_elastic_doc_id:
            metadata_iterator = GENERAL_INFORMATION_NOT_FLATTENED
            entity_iterator = GENERAL_ENTITIES
            elastic_document = EsClient.get_doc(
                index=GENERAL_ELASTICSEARCH_INDEX_NAME,
                doc_id=self.general_elastic_doc_id,
            )

        if elastic_document:
            document_metadata = elastic_document.get("_source", {}).get(
                "document_metadata", {}
            )
            if document_metadata:
                for metadata in metadata_iterator:
                    name = metadata["name"]
                    doc_metadata[name] = document_metadata[name]
                for entity in entity_iterator:
                    name = entity["name"]
                    doc_entity[name] = document_metadata[name]

        return {"doc_metadata": doc_metadata, "doc_entities": doc_entity}


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
