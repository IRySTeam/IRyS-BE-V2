import json
from typing import Optional, List

# from app.search.schemas import (
#     ElasticSearchResult, 
#     SemanticSearchRequest, 
#     SemanticSearchResponse
# )
from app.search.constants.search import DOMAIN_INDEXES
from app.search.enums.search import DomainEnum, FilterOperatorEnum
from app.search.schemas.elastic import MatchedDocument, SearchResult
from app.elastic.client import ElasticsearchClient

class SearchService:
    def __init__(self, algorithm, domain, scoring):
        self.algorithm = algorithm
        self.domain = DomainEnum.GENERAL # domain
        self.scoring = scoring

    def preprocess_query(self, query):
        """
        Refines raw user query by performing tokenization, stopword removal, stemming, lemmatization, and query expansion on it 
        [Input]
          - query: str
        [Output]
          - preprocessed query: str
        """
        processed_query = query # TODO: Call tokenization(self.raw_query)
        processed_query = query # TODO: Call stopword_removal(self.processed_query)
        processed_query = query # TODO: Call stemming(self.processed_query)
        processed_query = query # TODO: Call lemmatization(self.processed_query)
        processed_query = query # TODO: Call query_expansion(self.processed_query), Should we separate the query expansion process?
        return processed_query

    def normalize_search_result(self, data):
        search_result = SearchResult(result=[])
        for hit in data['hits']['hits']:
            matched_document = MatchedDocument(
                id=hit['_id'],
                score=hit['_score'],
                title=hit['_source']['title'],
                document_metadata={},
                document_entity={}
                # document_metadata=hit['_source']['document_metadata'],
                # document_entity=hit['_source']['document_entities']
            )
            search_result.result.append(matched_document)
        return search_result

    def elastic_keyword_search(self, query):
        """
        Executes first part of search, calls elastic search to perform keyword based search
        [Input]
          - query: Keyword based query
        [Output]
          - ElasticSearchResult
        """
        data = ElasticsearchClient().search_semantic(query, 'general-0001', 5,  ["title", "preprocessed_text"])
        return self.normalize_search_result(data)

    def evaluate_advanced_filter(self, search_result, advanced_filter):
        """
        Executes second part of search, filtering retrieved documents based on entity filters
        [Parameters]
          retrieved_documents: ? # TODO: Define a schema for elastic search retrieved documents
        [Returns]
          filtered_documents: ? # TODO: Should the schema be the same as retrieved documents or directly as API response schema?
        """
        advanced_search_result = search_result 

        # Evaluate basic filters
        if (bool(advanced_filter.basic_match)):
            for filter in advanced_filter.basic_match:
                advanced_search_result = self.evaluate_basic_filter(advanced_search_result, filter)

        # Evaluate semantic filters
        if (bool(advanced_filter['semantic_match'])):
            for filter in advanced_filter['semantic_match']:
                advanced_search_result = self.evaluate_semantic_filter(advanced_search_result, filter)
        return advanced_search_result
    
    def evaluate_basic_filter(self, search_result, filter):
        match filter.operator:
            case FilterOperatorEnum.IN:
                print('Got a reading of IN')
            case FilterOperatorEnum.NIN:
                print('Got a reading of NOT IN')
            case FilterOperatorEnum.EXI:
                print('Got a reading of EXISTS')
            case FilterOperatorEnum.NEXI:
                print('Got a reading of NOT EXISTS')
            case FilterOperatorEnum.EQ:
                print('Got a reading of EQUAL')
            case FilterOperatorEnum.NEQ:
                print('Got a reading of NOT EQUAL')
            case FilterOperatorEnum.GT:
                print('Got a reading of GREATER THAN')
            case FilterOperatorEnum.LT:
                print('Got a reading of LESS THAN')
            case FilterOperatorEnum.GTE:
                print('Got a reading of GREATER THAN EQUAL')
            case FilterOperatorEnum.LTE:
                print('Got a reading of LESS THAN EQUAL')
            case _:
                print('No operator match found')
        return search_result
    
    def evaluate_semantic_filter(self, search_result, filter):
        data = ElasticsearchClient().search_semantic(
            query=filter.value,
            index='general-0001', 
            size=filter.top_n,
            source=["title", "preprocessed_text"]
            # Add variable for text_vector based on key
        )
        return search_result

    def run_search(self, query, advanced_filter):
        """
        Calls query preprocessing, keyword search, and advanced filter methods
        [Parameters]
        [Returns]
          response: SemanticSearchResponse
        """
        processed_query = self.preprocess_query(query)
        # TODO: Call evaluate_advanced_filter()
        search_result = self.elastic_keyword_search(processed_query)
        return self.evaluate_advanced_filter(search_result, advanced_filter)
        
        # *tentative TODO: Transform result from last function call to response schema
