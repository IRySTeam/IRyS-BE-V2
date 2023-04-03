import json
from typing import Optional, List

from api.search.v1.request import SemanticSearchRequest
from api.search.v1.response import SemanticSearchResponse

from app.search.schemas.search_result import ElasticSearchResult
from app.search.constants.search import DOMAIN_INDEXES
from app.elastic.client import search_semantic

class SearchService:
    def __init__(self, request: SemanticSearchRequest):
        self.raw_query = request.query
        self.processed_query = ""
        self.algorithm = request.algorithm
        self.domain = request.domain
        self.scoring = request.scoring
        self.advanced_filter = request.advanced_filter

    def preprocess_query(self):
        """
        Refines raw user query by performing tokenization, stopword removal, stemming, lemmatization, and query expansion on it
        [I.S.]
          - self.raw_query is available from user request
          - transformation utility functions are available to call
        [F.S.]
          - self.processed_query is assigned with the final transformed query
        """
        self.processed_query = None # TODO: Call tokenization(self.raw_query)
        self.processed_query = None # TODO: Call stopword_removal(self.processed_query)
        self.processed_query = None # TODO: Call stemming(self.processed_query)
        self.processed_query = None # TODO: Call lemmatization(self.processed_query)
        self.processed_query = None # TODO: Call query_expansion(self.processed_query), Should we separate the query expansion process?

    def elastic_keyword_search(self):
        """
        Executes first part of search, calls elastic search to perform keyword based search
        [Parameters]
        [Returns]
          retrieved_documents: ElasticSearchResult
        """
        raw_data = search_semantic(self.processed_query, DOMAIN_INDEXES[self.domain])
        data = json.load(raw_data) # TODO: Possible data = retrieved documents, so might directly return data
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
        pass
    
    def run_search(self):
        """
        Calls query preprocessing, keyword search, and advanced filter methods
        [Parameters]
        [Returns]
          response: SemanticSearchResponse
        """
        # TODO: Call preprocess_query()
        # TODO: Call elastic_keyword_search()
        # TODO: Call evaluate_advanced_filter()
        # *tentative TODO: Transform result from last function call to response schema
