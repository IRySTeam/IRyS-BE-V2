from typing import Any, List, Mapping, Optional

from bert_serving.client import BertClient
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.exceptions import ApiError

from app.elastic.helpers import classify_error
from app.elastic.schemas import (
    ElasticCreateIndexResponse,
    ElasticIndexCat,
    ElasticIndexDetail,
    ElasticInfo,
)
from core.config import config
from core.exceptions.base import FailedDependencyException, NotFoundException


class ElasticsearchClient:
    """
    ElasticsearchClient is a singleton class that provides connection and several methods to interact
    with Elasticsearch.

    [Attributes]
      client: Elasticsearch -> Elasticsearch client instance.
    """

    def __init__(self) -> None:
        """
        Constructor of ElasticsearchClient class.
        """
        self.client = Elasticsearch(
            hosts=[
                {
                    "scheme": config.ELASTICSEARCH_SCHEME,
                    "host": config.ELASTICSEARCH_HOST,
                    "port": config.ELASTICSEARCH_PORT,
                }
            ],
            basic_auth=(config.ELASTICSEARCH_USER, config.ELASTICSEARCH_PASSWORD),
        )
        if config.ELASTICSEARCH_CLOUD.lower() == "true":
            self.client = Elasticsearch(
                cloud_id=config.ELASTICSEARCH_CLOUD_ID,
                basic_auth=(config.ELASTICSEARCH_USER, config.ELASTICSEARCH_PASSWORD),
            )

        self.indices_client = IndicesClient(self.client)

    def info(self) -> ElasticInfo:
        """
        Get the information about Elasticsearch cluster.
        [Returns]
          ElasticInfoResponseSchema: Information about Elasticsearch cluster.
        """
        try:
            return self.client.info()
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def list_indices(self, all: bool = False) -> List[ElasticIndexCat]:
        """
        List all indices in Elasticsearch.
        [Parameters]
          all: bool -> Whether to list auto-generated indices or not.
        [Returns]
          List[ElasticIndexCat]: List of indices.
        """
        try:
            indices: List[ElasticIndexCat] = list(
                self.client.cat.indices(format="json")
            )
            if not all:
                # Index that starts with "." is auto-generated by Elasticsearch.
                indices = [
                    index for index in indices if not index["index"].startswith(".")
                ]
            return indices
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def get_index(self, index: str) -> ElasticIndexDetail:
        """
        Get an index in Elasticsearch specified by index name.
        [Parameters]
          index: str -> Name of the index.
        [Returns]
        """
        try:
            indice = self.indices_client.get(index=index)
            return indice[index]
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def create_index(
        self,
        index_name: str,
        mappings: Optional[Mapping[str, Any]] = None,
        settings: Optional[Mapping[str, Any]] = None,
    ) -> ElasticCreateIndexResponse:
        """
        Create an index in Elasticsearch.
        [Parameters]
          index_name: str -> Name of the index.
          mappings: Optional[Mapping[str, Any]] -> Define how a document, and the fields it contains,
            are stored and indexed.
          settings: Optional[Mapping[str, Any]] -> Index configuration, there are static (unchangeable)
            and dynamic (changeable) settings.
        [Returns]
          ElasticCreateIndexResponse: Response of creating an index.
        """
        try:
            return self.indices_client.create(
                index=index_name, mappings=mappings, settings=settings
            )
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def update_index(
        self, index: str, settings: Mapping[str, Any]
    ) -> ObjectApiResponse[Any]:
        """
        Update an index dynamic settings in Elasticsearch.
        [Parameters]
            index: str -> Name of the index.
            settings: Mapping[str, Any] -> Index configuration that are changeable.
        [Returns]
            ObjectApiResponse[Any]: Response from Elasticsearch
        """
        try:
            return self.indices_client.put_settings(index=index, settings=settings)
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def delete_index(self, index: str) -> ObjectApiResponse[Any]:
        """
        Delete an index in Elasticsearch.
        [Parameters]
            index: str -> Name of the index.
        [Returns]
            ObjectApiResponse[Any]: Response from Elasticsearch
        """
        try:
            return self.indices_client.delete(index=index)
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def list_index_docs(self, index: str) -> List[dict]:
        """
        List all documents in an index in Elasticsearch.
        [Parameters]
          index: str -> Name of the index.
        [Returns]
          List[dict]: List of documents.
        """
        try:
            return self.client.search(index=index)["hits"]["hits"]
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def index_doc(self, index: str, doc: Mapping[str, Any]):
        """
        Index a document in Elasticsearch.
        [Parameters]
            index: str -> Name of the index.
            doc: Mapping[str, Any] -> Document to be indexed.
        [Returns]
            ObjectApiResponse[Any]: Response from Elasticsearch
        """
        try:
            return self.client.index(index=index, body=doc)
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def safe_delete_doc(self, index_name: str, doc_id: str) -> ObjectApiResponse[Any]:
        """
        Delete a document from an Elasticsearch index, but ignore if document does not exist.
        [Parameters]
            index_name: str -> Name of index that will contain the document
            doc_id: str -> ID of the document to be deleted in the corresponding index
        [Returns]
            ObjectApiResponse[Any]: Response from Elasticsearch
        """
        try:
            return self.client.delete(index=index_name, id=doc_id)
        except ApiError as e:
            error = classify_error(
                e,
                "Document with id: {} not found in index: {}".format(
                    doc_id, index_name
                ),
            )
            if isinstance(error, NotFoundException):
                print(error.message)
                return None
            raise error
        except Exception as e:
            raise FailedDependencyException(e)

    def delete_doc(self, index_name: str, doc_id: str) -> ObjectApiResponse[Any]:
        """
        Delete a document from an Elasticsearch index.
        [Parameters]
            index_name: str -> Name of index that will contain the document
            doc_id: str -> ID of the document to be deleted in the corresponding index
        [Returns]
            ObjectApiResponse[Any]: Response from Elasticsearch
        """
        try:
            return self.client.delete(index=index_name, id=doc_id)
        except ApiError as e:
            raise classify_error(
                e,
                "Document with id: {} not found in index: {}".format(
                    doc_id, index_name
                ),
            )
        except Exception as e:
            raise FailedDependencyException(e)

    def update_doc(self, index_name: str, doc_id: str, doc: Mapping[str, Any]):
        """
        Update a document from an Elasticsearch index.
        [Parameters]
            index_name: str -> Name of index that will contain the document
            doc_id: str -> ID of the document to be updated in the corresponding index
            doc: Mapping[str, Any] -> Document to be updated.
        [Returns]
            ObjectApiResponse[Any]: Response from Elasticsearch
        """
        try:
            return self.client.update(index=index_name, id=doc_id, body=doc)
        except ApiError as e:
            raise classify_error(
                e,
                "Document with id: {} not found in index: {}".format(
                    doc_id, index_name
                ),
            )
        except Exception as e:
            raise FailedDependencyException(e)

    def search_semantic(
        self, query: str, index: str, size: int, source: List[str], emb_vector: str
    ):
        """
        Retrieve documents from an Elasticsearch index based on an input query
        [Parameters]
          query: str -> User search prompt
          index_name: str -> Name of index that will be the base of the search
        """
        try:
            bc = BertClient(ip="bertserving", output_fmt="list", timeout=5000)
            query_vector = bc.encode([query])[0]

            script_query = {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": f'doc["{emb_vector}"].size() == 0 ? 0 : cosineSimilarity(params.query_vector, "{emb_vector}") + 1.0',
                        "params": {"query_vector": query_vector},
                    },
                }
            }

            return self.client.search(
                index=index, size=size, query=script_query, source={"includes": source}
            )

        except TimeoutError as e:
            raise e
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)  # TODO: Create new exception type
