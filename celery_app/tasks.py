import magic
import mimetypes
from binascii import a2b_base64
from typing import List, Dict, Any
from asgiref.sync import async_to_sync
from tika import parser

from core.config import config
from celery_app.main import celery
from app.document.enums.document import IndexingStatusEnum
from app.document.services import document_index_service, document_service
from app.preprocess import OCRUtil, PreprocessUtil
from app.classification import Classifier
from app.elastic import (
    EsClient,
    GENERAL_ELASTICSEARCH_INDEX_NAME,
    RECRUITMENT_ELASTICSEARCH_INDEX_NAME,
    SCIENTIFIC_ELASTICSEARCH_INDEX_NAME,
)
from bert_serving.client import BertClient


@celery.task(name="parsing", bind=True)
def parsing(
    self,
    document_id: int,
    document_title: str,
    file_content_str: str,
    with_ocr: bool = True,
) -> bool:
    """
    Celery task for parsing document. The parsing task will be split into 2 subtasks:
        1. Extracting text from document (parse document, OCR if necessary).
        2. Preprocessing text (case folding, tokenization, etc).
    [Parameters]
        document_id: int -> Document id.
        document_title: str -> Document title.
        file_content_str: str -> Decoded file content in base64.
        with_ocr: bool -> Whether to OCR the document or not.
    [Returns]
        bool -> True if parsing is successful.
    """
    try:
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.PARSING,
            current_task_id=self.request.id,
        )
        # Parsing content and predict extension.
        file_content = a2b_base64(file_content_str)
        file_extension = mimetypes.guess_extension(
            magic.from_buffer(file_content, mime=True)
        )
        if file_extension not in [".pdf", ".doc", ".docx", ".txt"]:
            raise Exception("Unsupported file type")
        file_text: str = parser.from_buffer(file_content)["content"]

        # TODO: Add check duplicate.
        with_ocr = True
        text_percentage = OCRUtil.get_text_percentage(file_content)
        if text_percentage < OCRUtil.TEXT_PERCENTAGE_THRESHOLD:
            with_ocr = False
        if file_extension == ".pdf" and with_ocr:
            file_text = OCRUtil.ocr(file_content)

        # Preprocess text.
        preprocessed_file_text = PreprocessUtil.preprocess(file_text)
        extraction.delay(
            document_id=document_id,
            document_title=document_title,
            file_content_str=file_content_str,
            file_raw_text=file_text,
            file_preprocessed_text=preprocessed_file_text,
        )
        return True
    except Exception as e:
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.FAILED,
            reason=str(e),
            current_task_id=None,
        )
        raise e


@celery.task(name="extraction", bind=True)
def extraction(
    self,
    document_id: int,
    document_title: str,
    file_content_str: str,
    file_raw_text: str,
    file_preprocessed_text: List[str],
) -> bool:
    """
    Celery task for extracting information from document. The extraction task will be split into 2
    subtasks:
        1. Predicting document type.
        2. Extracting high-level information from document such as metadata, entities, etc.
    [Parameters]
        document_id: int -> Document id.
        file_content_str: str -> Decoded file content in base64.
        file_raw_text: str -> Raw text from document.
        file_preprocessed_text: List[str] -> Preprocessed text from document.
    [Returns]
        bool -> True if extraction is successful
    """
    try:
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.EXTRACTING,
            current_task_id=self.request.id,
        )
        file_content = a2b_base64(file_content_str)
        document_label = Classifier.classify(texts=file_preprocessed_text)
        document_metadata = {}
        document_entities = {}
        indexing.delay(
            document_id=document_id,
            document_title=document_title,
            file_content_str=file_content_str,
            file_raw_text=file_raw_text,
            file_preprocessed_text=file_preprocessed_text,
            document_label=document_label,
            document_metadata=document_metadata,
            document_entities=document_entities,
        )
        return True
    except Exception as e:
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.FAILED,
            reason=str(e),
            current_task_id=None,
        )
        raise e


@celery.task(name="indexing", bind=True)
def indexing(
    self,
    document_id: int,
    document_title: str,
    file_content_str: str,
    file_raw_text: str,
    file_preprocessed_text: List[str],
    document_label: str,
    document_metadata: Dict[str, Any] = {},
    document_entities: Dict[str, Any] = {},
) -> bool:
    """
    Celelry task for indexing document. The indexing task will be split into 2 subtasks:
        1. Calculating document vector/feature/weight.
        2. Indexing document into Elasticsearch.
    [Parameters]
        document_id: int -> Document id.
        file_content_str: str -> Encoded file content in base64.
        file_raw_text: str -> Raw text from document.
        file_preprocessed_text: List[str] -> Preprocessed text from document.
        document_label: str -> Document category.
        document_metadata: Dict[str, Any] -> Metadata extracted from document.
        document_entities: Dict[str, Any] -> Entities extracted from document.
    [Returns]
        bool -> True if indexing is successful.
    """
    try:
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.INDEXING,
            current_task_id=self.request.id,
        )
        file_content = a2b_base64(file_content_str)
        # TODO: Instantiate bert client with longer max len sequence
        # TODO: Add embedding of longtext type data.
        bc = BertClient(
            ip=config.BERT_SERVER_IP,
            port=config.BERT_SERVER_PORT,
            port_out=config.BERT_SERVER_PORT_OUT,
            output_fmt="list",
        )
        embedding = bc.encode([" ".join(file_preprocessed_text)])

        doc = {
            "document_id": document_id,
            "title": document_title,
            "raw_text": file_raw_text,
            "preprocessed_text": " ".join(file_preprocessed_text),
            "text_vector": embedding[0],
            "document_label": document_label,
            "document_metadata": document_metadata,
            "document_entities": document_entities,
        }
        res = EsClient.index_doc(
            index=GENERAL_ELASTICSEARCH_INDEX_NAME,
            doc=doc,
        )
        elastic_doc_id = res["_id"]
        elastic_index_name = GENERAL_ELASTICSEARCH_INDEX_NAME
        if document_label == Classifier.LabelEnum.RESUME.value:
            res = EsClient.index_doc(
                index=RECRUITMENT_ELASTICSEARCH_INDEX_NAME,
                doc=doc,
            )
            elastic_doc_id = res["_id"]
            elastic_index_name = RECRUITMENT_ELASTICSEARCH_INDEX_NAME
        elif document_label == Classifier.LabelEnum.PAPER.value:
            res = EsClient.index_doc(
                index=SCIENTIFIC_ELASTICSEARCH_INDEX_NAME,
                doc=doc,
            )
            elastic_doc_id = res["_id"]
            elastic_index_name = SCIENTIFIC_ELASTICSEARCH_INDEX_NAME

        async_to_sync(document_service.update_document_celery)(
            id=document_id,
            elastic_doc_id=elastic_doc_id,
            elastic_index_name=elastic_index_name,
        )
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.SUCCESS,
            current_task_id=None,
        )
        return True
    except Exception as e:
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            status=IndexingStatusEnum.FAILED,
            reason=str(e),
            current_task_id=None,
        )
        raise e
