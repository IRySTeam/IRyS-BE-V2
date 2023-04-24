import json
import re
from typing import Optional, List

# from app.search.schemas import (
#     ElasticSearchResult, 
#     SemanticSearchRequest, 
#     SemanticSearchResponse
# )
from app.search.constants.search import DOMAIN_INDEXES
from app.search.enums.search import DomainEnum, FilterOperatorEnum
from app.search.schemas.elastic import MatchedDocument, SearchResult
from app.search.schemas.advanced_search import AdvancedFilterConditions
from app.elastic.client import ElasticsearchClient
from app.preprocess import PreprocessUtil

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
        return " ".join(PreprocessUtil().preprocess(query))

    def normalize_search_result(self, data):
        search_result = SearchResult(result=[])
        for hit in data['hits']['hits']:
            matched_document = MatchedDocument(
                id=hit['_id'],
                score=hit['_score'],
                title=hit['_source']['title'],
                document_metadata=hit['_source']['document_metadata'],
                document_entity=hit['_source']['document_entities']
            )
            search_result.result.append(matched_document)
        return search_result

    def elastic_keyword_search(self, query, domain):
        """
        Executes first part of search, calls elastic search to perform keyword based search
        [Input]
          - query: Keyword based query
        [Output]
          - ElasticSearchResult
        """
        data = ElasticsearchClient().search_semantic(
            query=query, 
            index=f'{domain.value}-0001', 
            size=5,  
            source=["title", "preprocessed_text", "document_metadata", "document_entities"], 
            emb_vector="text_vector"
        )
        return self.normalize_search_result(data)

    def evaluate_advanced_filter(self, search_result, domain, advanced_filter):
        """
        Executes second part of search, filtering retrieved documents based on entity filters
        [Parameters]
          retrieved_documents: ? # TODO: Define a schema for elastic search retrieved documents
        [Returns]
          filtered_documents: ? # TODO: Should the schema be the same as retrieved documents or directly as API response schema?
        """
        advanced_search_result = search_result 

        # Evaluate advanced filters
        if (bool(advanced_filter.match)):
            for filter in advanced_filter.match:
                advanced_search_result = self.evaluate_filter(advanced_search_result, domain, filter)

        return advanced_search_result
    
    def evaluate_filter(self, search_result: MatchedDocument, domain: DomainEnum, filter: AdvancedFilterConditions):
        """
        Performs filtering using basic operators from retrieved documents
        [Parameters]
          search_result: MatchedDocument
          filter: AdvancedFilterConditions
        [Returns]
          MatchedDocument
        """
        match filter.operator:
            case FilterOperatorEnum.IN:
                return self.evaluate_in_filter(search_result, filter)
            case FilterOperatorEnum.NIN:
                return self.evaluate_nin_filter(search_result, filter)
            case FilterOperatorEnum.EXI:
                return self.evaluate_exi_filter(search_result, filter)
            case FilterOperatorEnum.NEXI:
                return self.evaluate_nexi_filter(search_result, filter)
            case FilterOperatorEnum.EQ:
                return self.evaluate_eq_filter(search_result, filter)
            case FilterOperatorEnum.NEQ:
                return self.evaluate_neq_filter(search_result, filter)
            case FilterOperatorEnum.GT:
                # TODO: Check for sufficient values:
                #   - numerical values (check and convert) --> Is it okay to just generalize everything as floats?
                #   - date values (check and convert) --> How to deal with the various ways of date writing?
                #   - if not sufficient raise 400 error
                #   - if sufficient then proceed to filter
                print('Got a reading of GREATER THAN')
            case FilterOperatorEnum.LT:
                print('Got a reading of LESS THAN')
            case FilterOperatorEnum.GTE:
                print('Got a reading of GREATER THAN EQUAL')
            case FilterOperatorEnum.LTE:
                print('Got a reading of LESS THAN EQUAL')
            case FilterOperatorEnum.CON:
                search_result.result = [d for d in search_result.result 
                                        if d.document_metadata.get(filter.key) 
                                            is not None
                                        and filter.value in d.document_metadata.get(filter.key)]
            case FilterOperatorEnum.NCON:
                print('Got a reading of NOT CONTAINS')
            case FilterOperatorEnum.REG:
                search_result.result = [d for d in search_result.result 
                                        if d.document_metadata.get(filter.key) 
                                            is not None
                                        and re.search(filter.value) is not None]
            case FilterOperatorEnum.SEM:
                return self.evaluate_semantic_filter(search_result, domain, filter)
                print('Got a reading of SEMANTIC SEARCH')
            case _:
                print('No operator match found')
        return search_result
    
    def evaluate_in_filter(self, search_result: MatchedDocument, filter: AdvancedFilterConditions):
        """
        Performs filtering using IN operator
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    in filter.value]
    
    def evaluate_nin_filter(self, search_result: MatchedDocument, filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT IN operator
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    not in filter.value]
    
    def evaluate_exi_filter(self, search_result: MatchedDocument, filter: AdvancedFilterConditions):
        """
        Performs filtering using EXISTS operator
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None]
    
    def evaluate_nexi_filter(self, search_result: MatchedDocument, filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT EXISTS operator
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is None]
    
    def evaluate_eq_filter(self, search_result: MatchedDocument, filter: AdvancedFilterConditions):
        """
        Performs filtering using EQUAL operator
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """ 
        return [d for d in search_result.result 
            if d.document_metadata.get(filter.key) 
                == filter.value]
    
    def evaluate_neq_filter(self, search_result: MatchedDocument, filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT EQUAL operator
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    != filter.value]
    
    def evaluate_semantic_filter(self, search_result: MatchedDocument, domain: DomainEnum, filter: AdvancedFilterConditions):
        """
        Performs filtering using semantic search on specific metadata and entities from retrieved documents
        [Parameters]
          search_result: MatchedDocument
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        data = ElasticsearchClient().search_semantic(
            query=filter.value,
            index=f'{domain}-0001', 
            size=filter.top_n,
            source=["title", "preprocessed_text", "document_metadata", "document_entities"],
            emb_vector=f"{filter.key}_vector"
        )
        return search_result

    def run_search(self, query, domain, advanced_filter):
        """
        Calls query preprocessing, keyword search, and advanced filter methods
        [Parameters]
        [Returns]
          response: SemanticSearchResponse
        """
        processed_query = self.preprocess_query(query)
        search_result = self.elastic_keyword_search(processed_query, domain)
        search_result.result = self.evaluate_advanced_filter(search_result, domain, advanced_filter)
    
        return search_result
        
        # *tentative TODO: Transform result from last function call to response schema
