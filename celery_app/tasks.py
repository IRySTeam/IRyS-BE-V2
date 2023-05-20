import mimetypes
from typing import Any, Dict, List, Union

import magic
from asgiref.sync import async_to_sync
from bert_serving.client import BertClient
from tika import parser

from app.classification import Classifier, LabelEnum
from app.document.enums.document import IndexingStatusEnum
from app.document.services import document_index_service, document_service
from app.elastic import (
    GENERAL_ELASTICSEARCH_INDEX_NAME,
    RECRUITMENT_ELASTICSEARCH_INDEX_NAME,
    SCIENTIFIC_ELASTICSEARCH_INDEX_NAME,
    EsClient,
)
from app.extraction import InformationExtractor
from app.extraction.domains.recruitment import RECRUITMENT_INFORMATION
from app.extraction.domains.scientific import SCIENTIFIC_INFORMATION
from app.preprocess import OCRUtil, PreprocessUtil
from celery_app.main import celery, text_encoding_manager
from core.config import config
from core.utils import GCStorage


@celery.task(
    name="parsing",
    bind=True,
    rate_limit="2/s",
)
def parsing(
    self,
    document_id: int,
    document_title: str,
    document_url: str,
    document_label: str = None,
    document_title_fixed: bool = False,
) -> bool:
    """
    Celery task for parsing document. The parsing task will be split into 2 subtasks:
        1. Extracting text from document (parse document, OCR if necessary).
        2. Preprocessing text (case folding, tokenization, etc).
    [Parameters]
        document_id: int -> Document id.
        document_title: str -> Document title.
        document_url: str -> Document url.
        document_label: str -> Document predefined label, used when manually changing label.
    [Returns]
        bool -> True if parsing is successful.
    """
    try:
        # Check if provided document label is valid.
        if document_label and document_label not in set(
            enum.value for enum in LabelEnum
        ):
            raise Exception("Invalid document label")

        # Update indexing status.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "reason": None,
                "status": IndexingStatusEnum.PARSING,
                "current_task_id": self.request.id,
            },
        )
        file_bytes = GCStorage().get_file(document_url)

        # Parsing content and predict extension.
        file_extension = mimetypes.guess_extension(
            magic.from_buffer(file_bytes, mime=True)
        )
        if file_extension not in [".pdf", ".doc", ".docx", ".txt"]:
            raise Exception("Unsupported file type")
        file_text: str = parser.from_buffer(file_bytes)["content"]

        with_ocr = False
        text_percentage = OCRUtil.get_text_percentage(file_bytes)
        if text_percentage < OCRUtil.TEXT_PERCENTAGE_THRESHOLD:
            with_ocr = True
        if file_extension == ".pdf" and with_ocr:
            file_text = OCRUtil.ocr(file_bytes)

        # Preprocess text and do extraction.
        preprocessed_file_text = PreprocessUtil.preprocess(file_text)
        extraction.delay(
            document_id=document_id,
            document_title=document_title,
            document_url=document_url,
            document_label=document_label,
            document_title_fixed=document_title_fixed,
            with_ocr=with_ocr,
            file_raw_text=file_text,
            file_preprocessed_text=preprocessed_file_text,
        )
        return True
    except Exception as e:
        # Update indexing status to failed.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "status": IndexingStatusEnum.FAILED,
                "reason": str(e),
                "current_task_id": None,
            },
        )
        raise e


@celery.task(
    name="extraction",
    bind=True,
    rate_limit="2/s",
)
def extraction(
    self,
    document_id: int,
    document_title: str,
    document_url: str,
    document_label: str = None,
    document_title_fixed: bool = False,
    with_ocr: bool = False,
    file_raw_text: str = "",
    file_preprocessed_text: List[str] = [],
) -> bool:
    """
    Celery task for extracting information from document. The extraction task will be split into 2
    subtasks:
        1. Predicting document type.
        2. Extracting high-level information from document such as metadata, entities, etc.
    [Parameters]
        document_id: int -> Document id.
        document_title: str -> Document title.
        document_url: str -> Document url.
        file_raw_text: str -> Raw text from document.
        file_preprocessed_text: List[str] -> Preprocessed text from document.
        with_ocr: bool -> Whether document is parsed with OCR or not.
    [Returns]
        bool -> True if extraction is successful
    """
    try:
        print("A")
        # Update indexing status to extracting.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "reason": None,
                "status": IndexingStatusEnum.EXTRACTING,
                "current_task_id": self.request.id,
            },
        )
        print("B")
        file_bytes = GCStorage().get_file(document_url)
        print("C")

        # Classify document type and extract general information from document.
        extractor = InformationExtractor(domain="general")
        print("D")
        general_document_metadata = extractor.extract(file_bytes, file_raw_text)
        print("E")
        document_metadata = {}
        document_label = document_label or Classifier.classify(
            texts=file_preprocessed_text
        )
        print("F")

        # Extract information on domain-specific document.
        domain = None
        if document_label == LabelEnum.RESUME.value:
            domain = "recruitment"
            print("G1")
        elif document_label == LabelEnum.PAPER.value:
            domain = "scientific"
            print("G2")
        if domain:
            extractor = InformationExtractor(domain=domain)
            print("H")
            if with_ocr:
                document_metadata = extractor.extract(file_bytes, file_raw_text)
                print("I1")
            else:
                document_metadata = extractor.extract(file_bytes)
                print("I2")

        # Update document metadata on database.
        mimetype = document_metadata.get("mimetype", None)
        print("J")
        extension = document_metadata.get("extension", None)
        print("K")
        size = document_metadata.get("size", None)
        print("L")
        if not document_title_fixed:
            document_title = document_metadata.get("title", None) or document_title
        print("M")

        # Update document in database according to extracted metadata and do indexing.
        async_to_sync(document_service.update_document_celery)(
            id=document_id,
            params={
                "title": document_title,
                "mimetype": mimetype,
                "extension": extension,
                "size": size,
            },
        )
        print("N")
        indexing.delay(
            document_id=document_id,
            document_title=document_title,
            document_label=document_label,
            document_metadata=document_metadata,
            general_document_metadata=general_document_metadata,
            file_raw_text=file_raw_text,
            file_preprocessed_text=file_preprocessed_text,
        )
        print("O")
        return True
    except Exception as e:
        # Turn indexing status to failed if extraction failed.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "status": IndexingStatusEnum.FAILED,
                "reason": str(e),
                "current_task_id": None,
            },
        )
        raise e


@celery.task(
    name="indexing",
    bind=True,
    rate_limit="2/s",
)
def indexing(
    self,
    document_id: int,
    document_title: str,
    document_label: str,
    document_metadata: Dict[str, Any] = {},
    general_document_metadata: Dict[str, Any] = {},
    file_raw_text: str = "",
    file_preprocessed_text: List[str] = [],
) -> bool:
    """
    Celelry task for indexing document. The indexing task will be split into 2 subtasks:
        1. Calculating document vector/feature/weight.
        2. Indexing document into Elasticsearch.
    [Parameters]
        document_id: int -> Document id.
        file_raw_text: str -> Raw text from document.
        file_preprocessed_text: List[str] -> Preprocessed text from document.
        document_label: str -> Document category.
        document_metadata: Dict[str, Any] -> Metadata extracted from document.
        general_document_metadata: Dict[str, Any] -> Metadata with general domain.
    [Returns]
        bool -> True if indexing is successful.
    """
    try:
        # Update indexing status.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "reason": None,
                "status": IndexingStatusEnum.INDEXING,
                "current_task_id": self.request.id,
            },
        )

        # Setup dummy variable.
        general_elastic_doc_id = None
        elastic_doc_id = None
        elastic_index_name = None

        # Prepare document to be indexed.
        bc = BertClient(
            ip=config.BERT_SERVER_IP,
            port=config.BERT_SERVER_PORT,
            port_out=config.BERT_SERVER_PORT_OUT,
            output_fmt="list",
        )
        # Index the general domain document into Elasticsearch.
        # embedding = bc.encode([" ".join(file_preprocessed_text)])

        match document_label:
            case LabelEnum.RESUME.value:
                domain = "recruitment"
            case LabelEnum.PAPER.value:
                domain = "scientific"
            case _:
                domain = "general"
        embedding = text_encoding_manager.get_encoder(domain=domain).encode(
            " ".join(file_preprocessed_text)
        )

        doc = {
            "document_id": document_id,
            "title": document_title,
            "raw_text": file_raw_text,
            "preprocessed_text": " ".join(file_preprocessed_text),
            "text_vector": embedding,
            "document_label": document_label,
            "document_metadata": general_document_metadata,
        }
        res = EsClient.index_doc(
            index=GENERAL_ELASTICSEARCH_INDEX_NAME,
            doc=doc,
        )
        general_elastic_doc_id = res["_id"]

        # Index document into Elasticsearch according to document type.
        doc["document_metadata"] = document_metadata
        if document_label != LabelEnum.OTHER.value:
            metadata_info = (
                SCIENTIFIC_INFORMATION
                if document_label == LabelEnum.PAPER.value
                else RECRUITMENT_INFORMATION
            )
            for dict in metadata_info:
                name = dict["name"]
                type = dict["type"]
                # Type of metadata checking, if type contains "semantic" then we need to generate vector for the metadata.
                preprocessed_metadata = None
                if type == "semantic text":
                    metadata_value: Union[str, List[str]] = document_metadata.get(
                        name, ""
                    )
                    preprocessed_metadata = PreprocessUtil.preprocess(metadata_value)

                # Generate vector for metadata.
                if preprocessed_metadata:
                    metadata_embedding = text_encoding_manager.get_encoder(
                        domain=domain
                    ).encode(" ".join(file_preprocessed_text))
                    doc["document_metadata"][name] = {
                        "text": metadata_value,
                        "text_vector": metadata_embedding,
                    }
                elif not preprocessed_metadata and type == "semantic text":
                    doc["document_metadata"][name] = {
                        "text": "",
                        "text_vector": [0.0 for _ in range(768)],
                    }

            res = EsClient.index_doc(
                index=SCIENTIFIC_ELASTICSEARCH_INDEX_NAME
                if document_label == LabelEnum.PAPER.value
                else RECRUITMENT_ELASTICSEARCH_INDEX_NAME,
                doc=doc,
            )
            elastic_doc_id = res["_id"]
            elastic_index_name = (
                SCIENTIFIC_ELASTICSEARCH_INDEX_NAME
                if document_label == LabelEnum.PAPER.value
                else RECRUITMENT_ELASTICSEARCH_INDEX_NAME
            )

        # Update document elasticsearch related metadata and indexing status on database.
        async_to_sync(document_service.update_document_celery)(
            id=document_id,
            params={
                "general_elastic_doc_id": general_elastic_doc_id,
                "elastic_doc_id": elastic_doc_id,
                "elastic_index_name": elastic_index_name,
            },
        )
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "reason": None,
                "status": IndexingStatusEnum.SUCCESS,
                "current_task_id": None,
            },
        )
        return True
    except Exception as e:
        # Turn indexing status to failed if indexing failed.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "status": IndexingStatusEnum.FAILED,
                "reason": str(e),
                "current_task_id": None,
            },
        )

        # Delete document from Elasticsearch if indexing failed.
        if general_elastic_doc_id:
            EsClient.delete_doc(
                index_name=GENERAL_ELASTICSEARCH_INDEX_NAME,
                doc_id=general_elastic_doc_id,
            )
        if elastic_doc_id and elastic_index_name:
            EsClient.delete_doc(
                index_name=elastic_index_name,
                doc_id=elastic_doc_id,
            )
        raise e
