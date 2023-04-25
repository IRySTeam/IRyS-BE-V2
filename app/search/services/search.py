# from app.search.schemas import (
#     ElasticSearchResult,
#     SemanticSearchRequest,
#     SemanticSearchResponse
# )
from app.elastic.client import ElasticsearchClient
from app.search.enums.search import DomainEnum


class SearchService:
    def __init__(self, algorithm, domain, scoring):
        self.algorithm = algorithm
        self.domain = DomainEnum.GENERAL  # domain
        self.scoring = scoring

    def preprocess_query(self, query):
        """
        Refines raw user query by performing tokenization, stopword removal, stemming, lemmatization, and query expansion on it
        [Input]
          - query: str
        [Output]
          - preprocessed query: str
        """
        processed_query = query  # TODO: Call tokenization(self.raw_query)
        processed_query = query  # TODO: Call stopword_removal(self.processed_query)
        processed_query = query  # TODO: Call stemming(self.processed_query)
        processed_query = query  # TODO: Call lemmatization(self.processed_query)
        processed_query = query  # TODO: Call query_expansion(self.processed_query), Should we separate the query expansion process?
        return processed_query

    def elastic_keyword_search(self, query):
        """
        Executes first part of search, calls elastic search to perform keyword based search
        [Input]
          -
        [Output]
          - retrieved_documents: ElasticSearchResult
        """
        data = ElasticsearchClient().search_semantic(
            query, "general-0001", 5, ["title", "preprocessed_text"]
        )
        # TODO: Possible data = retrieved documents, so might directly return data
        # retrieved_documents = Call some function to parse data into ElasticSearchResult
        return data

    def evaluate_advanced_filter(self, retrived_documents):
        """
        Executes second part of search, filtering retrieved documents based on entity filters
        [Parameters]
          retrieved_documents: ? # TODO: Define a schema for elastic search retrieved documents
        [Returns]
          filtered_documents: ? # TODO: Should the schema be the same as retrieved documents or directly as API response schema?
        """
        filtered_documents = (
            {}
        )  # TODO: Make this into yet another new schema or just use the existing final response schema?
        if bool(self.advanced_filter):
            pass  # TODO: Filter retrieved_documents according to the advanced filter
        return filtered_documents

    def run_search(self, query, advanced_filter):
        """
        Calls query preprocessing, keyword search, and advanced filter methods
        [Parameters]
        [Returns]
          response: SemanticSearchResponse
        """
        processed_query = self.preprocess_query(query)
        # TODO: Call evaluate_advanced_filter()
        return self.elastic_keyword_search(processed_query)
        # *tentative TODO: Transform result from last function call to response schema
