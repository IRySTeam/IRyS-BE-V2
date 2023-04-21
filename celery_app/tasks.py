import magic
import mimetypes
from binascii import a2b_base64
from typing import List, Union, Dict, Any
from asgiref.sync import async_to_sync
from tika import parser

from celery_app.main import celery
from app.preprocess import OCRUtil, PreprocessUtil
from app.classification import Classifier
from app.elastic import EsClient, GENERAL_ELASTICSEARCH_INDEX_NAME
from bert_serving.client import BertClient


@celery.task(name="tasks.parsing")
def parsing(
    document_id: int, document_title: str, file_content_str: str, with_ocr: bool = True
) -> Union[bool, str]:
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
        Union[bool, str] -> True if parsing is successful, else error message.
    """
    try:
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.PARSING,
        # )
        # Parsing content and predict extension.
        file_content = a2b_base64(file_content_str)
        file_extension = mimetypes.guess_extension(
            magic.from_buffer(file_content, mime=True)
        )
        if file_extension not in [".pdf", ".doc", ".docx", ".txt"]:
            # TODO: Raise error unsupported file type
            pass
        file_text: str = parser.from_buffer(file_content)["content"]
        # TODO: Check if document is scanned, if so, OCR it regardless of with_ocr boolean status.
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
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.FAILED,
        #     reason=str(e)
        # )
        print(e)
        raise e


@celery.task(name="tasks.extracting")
def extraction(
    document_id: int,
    document_title: str,
    file_content_str: str,
    file_raw_text: str,
    file_preprocessed_text: List[str],
) -> Union[bool, str]:
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
        Union[bool, str] -> True if extraction is successful, else error message.
    """
    try:
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.EXTRACTING,
        # )
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
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.FAILED,
        #     reason=str(e)
        # )
        print(e)
        raise e


@celery.task(name="tasks.indexing")
def indexing(
    document_id: int,
    document_title: str,
    file_content_str: str,
    file_raw_text: str,
    file_preprocessed_text: List[str],
    document_label: str,
    document_metadata: Dict[str, Any] = {},
    document_entities: Dict[str, Any] = {},
):
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
        Union[bool, str] -> True if indexing is successful, else error message.
    """
    try:
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.INDEXING,
        # )
        file_content = a2b_base64(file_content_str)
        # TODO: Add bertclient data to env file.
        bc = BertClient(ip="bertserving", output_fmt="list")
        embedding = bc.encode([" ".join(file_preprocessed_text)])
        # TODO: Index document according to document type.
        EsClient.index_doc(
            index=GENERAL_ELASTICSEARCH_INDEX_NAME,
            doc={
                "document_id": document_id,
                "title": document_title,
                "raw_text": file_raw_text,
                "preprocessed_text": " ".join(file_preprocessed_text),
                "text_vector": embedding[0],
                "document_label": document_label,
                "document_metadata": document_metadata,
                "document_entities": document_entities,
            },
        )
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.SUCCESS,
        # )
        return True
    except Exception as e:
        # TODO: Fix context error.
        # async_to_sync(document_index_service.update_indexing_status)(
        #     doc_id=document_id,
        #     status=IndexingStatusEnum.FAILED,
        #     reason=str(e)
        # )
        print(e)
        raise e
