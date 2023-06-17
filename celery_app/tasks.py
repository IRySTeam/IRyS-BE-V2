import datetime
import mimetypes
from typing import Any, Dict, List, Union

import magic
from asgiref.sync import async_to_sync
from bert_serving.client import BertClient
from tika import parser
from tzlocal import get_localzone

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
from app.search.services.text_encoding_manager import TextEncodingManager
from celery_app.main import celery
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
        print(
            "[PARSING] task of document [{}] is started at [{}]".format(
                document_id,
                datetime.datetime.now()
                .astimezone(get_localzone())
                .strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
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
        if file_extension == ".pdf":
            text_percentage = OCRUtil.get_text_percentage(file_bytes)
            if text_percentage < OCRUtil.TEXT_PERCENTAGE_THRESHOLD:
                with_ocr = True
            if with_ocr:
                file_text = OCRUtil.ocr(file_bytes)

        # Preprocess text and do extraction.
        preprocessed_file_text = PreprocessUtil.preprocess(file_text)
        print(
            "[PARSING] task of document [{}] is finished at [{}]".format(
                document_id,
                datetime.datetime.now()
                .astimezone(get_localzone())
                .strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
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
        print(
            "[EXTRACTION] task of document [{}] is started at [{}]".format(
                document_id,
                datetime.datetime.now()
                .astimezone(get_localzone())
                .strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        # Update indexing status to extracting.
        async_to_sync(document_index_service.update_indexing_status_celery)(
            doc_id=document_id,
            params={
                "reason": None,
                "status": IndexingStatusEnum.EXTRACTING,
                "current_task_id": self.request.id,
            },
        )
        file_bytes = GCStorage().get_file(document_url)

        # Classify document type and extract general information from document.
        extractor = InformationExtractor(domain="general")
        general_document_metadata = extractor.extract(file_bytes, file_raw_text)
        document_metadata = {}
        document_label = document_label or Classifier.classify(
            texts=file_preprocessed_text
        )

        # Extract information on domain-specific document.
        domain = None
        if document_label == LabelEnum.RESUME.value:
            domain = "recruitment"
        elif document_label == LabelEnum.PAPER.value:
            domain = "scientific"
        if domain:
            extractor = InformationExtractor(domain=domain)
            if with_ocr:
                document_metadata = extractor.extract(file_bytes, file_raw_text)
            else:
                document_metadata = extractor.extract(file_bytes)

        # Update document metadata on database.
        mimetype = document_metadata.get("mimetype", None)
        extension = document_metadata.get("extension", None)
        size = document_metadata.get("size", None)
        if not document_title_fixed:
            document_title = document_metadata.get("title", None) or document_title

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
        print(
            "[EXTRACTION] task of document [{}] is finished at [{}]".format(
                document_id,
                datetime.datetime.now()
                .astimezone(get_localzone())
                .strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        
        for models in ["paraphrase", "msmarco"]:
            indexing.delay(
                document_id=document_id,
                document_title=document_title,
                document_label=document_label,
                document_metadata=document_metadata,
                general_document_metadata=general_document_metadata,
                file_raw_text=file_raw_text,
                file_preprocessed_text=file_preprocessed_text,
                is_paraphrase_model=models=="paraphrase",
            )

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
    is_paraphrase_model: bool = False,
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
        print(
            "[INDEXING] task of document [{}] is started at [{}]".format(
                document_id,
                datetime.datetime.now()
                .astimezone(get_localzone())
                .strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        text_encoding_manager = TextEncodingManager()
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

        # if is_paraphrase_model:
        #     embedding = bc.encode([" ".join(file_preprocessed_text)])

        doc = {
            "document_id": document_id,
            "title": document_title,
            "raw_text": file_raw_text,
            "preprocessed_text": " ".join(file_preprocessed_text),
            "text_vector": embedding,
            "document_label": document_label,
            "document_metadata": general_document_metadata,
        }
        if is_paraphrase_model:
            general_index_name = GENERAL_ELASTICSEARCH_INDEX_NAME.replace("msmarco", "paraphrase")
        else:
            general_index_name = GENERAL_ELASTICSEARCH_INDEX_NAME

        res = EsClient.index_doc(
            index=general_index_name,
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

            elastic_index_name = (
                SCIENTIFIC_ELASTICSEARCH_INDEX_NAME
                if document_label == LabelEnum.PAPER.value
                else RECRUITMENT_ELASTICSEARCH_INDEX_NAME
            )
            if is_paraphrase_model:
                elastic_index_name = elastic_index_name.replace("msmarco", "paraphrase")

            res = EsClient.index_doc(
                index=elastic_index_name,
                doc=doc,
            )
            elastic_doc_id = res["_id"]
            
            
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

        # Write current timestamp.
        print(
            "[INDEXING] task of document [{}] is finished at [{}]".format(
                document_id,
                datetime.datetime.now()
                .astimezone(get_localzone())
                .strftime("%Y-%m-%d %H:%M:%S"),
            )
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

        if is_paraphrase_model:
            general_index_name = GENERAL_ELASTICSEARCH_INDEX_NAME.replace("msmarco", "paraphrase")
        else:
            general_index_name = GENERAL_ELASTICSEARCH_INDEX_NAME
        # Delete document from Elasticsearch if indexing failed.
        if general_elastic_doc_id:
            EsClient.delete_doc(
                index_name=general_index_name,
                doc_id=general_elastic_doc_id,
            )
        if elastic_doc_id and elastic_index_name:
            EsClient.delete_doc(
                index_name=elastic_index_name,
                doc_id=elastic_doc_id,
            )
        raise e
