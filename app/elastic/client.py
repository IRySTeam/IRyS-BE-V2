from typing import Mapping, Optional, Any, List
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ApiError
from elasticsearch.client import IndicesClient

from core.config import config
from core.exceptions.base import FailedDependencyException, NotFoundException
from app.elastic.helpers import classify_error
from app.elastic.configuration import (
    GENERAL_ELASTICSEARCH_INDEX_SETTINGS,
    GENERAL_ELASTICSEARCH_INDEX_MAPPINGS,
)
from app.elastic.schemas import (
    ElasticInfo,
    ElasticIndexCat,
    ElasticIndexDetail,
    ElasticCreateIndexResponse,
)
from bert_serving.client import BertClient

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
        mapping: Optional[Mapping[str, Any]] = None,
        settings: Optional[Mapping[str, Any]] = None,
    ) -> ElasticCreateIndexResponse:
        """
        Create an index in Elasticsearch.
        [Parameters]
          index_name: str -> Name of the index.
          mapping: Optional[Mapping[str, Any]] -> Define how a document, and the fields it contains,
            are stored and indexed.
          settings: Optional[Mapping[str, Any]] -> Index configuration, there are static (unchangeable)
            and dynamic (changeable) settings.
        [Returns]
          ElasticCreateIndexResponse: Response of creating an index.
        """
        try:
            if mapping is None or mapping == {}:
                mapping = GENERAL_ELASTICSEARCH_INDEX_MAPPINGS
            if settings is None or settings == {}:
                settings = GENERAL_ELASTICSEARCH_INDEX_SETTINGS
            return self.indices_client.create(
                index=index_name, mappings=mapping, settings=settings
            )
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def update_index(self, index: str, settings: Mapping[str, Any]):
        """
        Update an index dynamic settings in Elasticsearch.
        [Parameters]
          index: str -> Name of the index.
          settings: Mapping[str, Any] -> Index configuration that are changeable.
        [Returns]
        """
        try:
            self.indices_client.put_settings(index=index, settings=settings)
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def delete_index(self, index: str) -> None:
        """
        Delete an index in Elasticsearch.
        [Parameters]
          index: str -> Name of the index.
        """
        try:
            self.indices_client.delete(index=index)
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
        """
        try:
            return self.client.index(index=index, body=doc)
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)

    def search_semantic(self, query: str, index: str, size: int, source: List[str]):
        """
        Retrieve documents from an Elasticsearch index based on an input query
        [Parameters]
          query: str -> User search prompt
          index_name: str -> Name of index that will be the base of the search
        """
        try:
            bc = BertClient(output_fmt="list", timeout=5000)
            query_vector = bc.encode([query])[0]
            
            script_query = {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "doc[\"text_vector\"].size() == 0 ? 0 : cosineSimilarity(params.query_vector, \"text_vector\") + 1.0",
                        "params": {"query_vector": query_vector}, 
                    },
                }
            }

            return self.client.search(
                index=index, 
                size=size,
                query=script_query,
                source={"includes": source}
            )
        
        except TimeoutError as e:
            raise e
        except ApiError as e:
            raise classify_error(e)
        except Exception as e:
            raise FailedDependencyException(e)  # TODO: Create new exception type
