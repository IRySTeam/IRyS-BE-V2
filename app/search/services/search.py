import json
import re
from typing import Optional, List
from datetime import datetime

# from app.search.schemas import (
#     ElasticSearchResult, 
#     SemanticSearchRequest, 
#     SemanticSearchResponse
# )
from app.search.constants.search import DOMAIN_INDEXES
from app.search.enums.search import DomainEnum, FilterOperatorEnum
from app.search.schemas.elastic import MatchedDocument, SearchResult
from app.search.schemas.advanced_search import AdvancedFilterConditions
from app.search.schemas.search import SemanticSearchResponseSchema
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
                document_metadata=hit['_source']['document_metadata']
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
            source=["title", "preprocessed_text", "document_metadata"], 
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
            print("went in")
            for filter in advanced_filter.match:
                advanced_search_result.result = self.evaluate_filter(advanced_search_result, domain, filter)

        return advanced_search_result
    
    def evaluate_filter(self, search_result: List[MatchedDocument], domain: DomainEnum, filter: AdvancedFilterConditions):
        """
        Performs filtering using basic operators from retrieved documents
        [Parameters]
          search_result: List[MatchedDocument]
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
                return self.evaluate_gt_filter(search_result, filter)
            case FilterOperatorEnum.LT:
                return self.evaluate_lt_filter(search_result, filter)
            case FilterOperatorEnum.GTE:
                return self.evaluate_gte_filter(search_result, filter)
            case FilterOperatorEnum.LTE:
                return self.evaluate_lte_filter(search_result, filter)
            case FilterOperatorEnum.CON:
                return self.evaluate_con_filter(search_result, filter)
            case FilterOperatorEnum.NCON:
                return self.evaluate_ncon_filter(search_result, filter)
            case FilterOperatorEnum.REG:
                return self.evaluate_reg_filter(search_result, filter)
            case FilterOperatorEnum.SEM:
                return self.evaluate_semantic_filter(search_result, domain, filter)
            case _:
                print('No operator match found')
        return search_result
    
    def evaluate_in_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using IN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    in filter.value]
    
    def evaluate_nin_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT IN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    not in filter.value]
    
    def evaluate_exi_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using EXISTS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None]
    
    def evaluate_nexi_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT EXISTS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is None]
    
    def evaluate_eq_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """ 
        return [d for d in search_result.result 
            if d.document_metadata.get(filter.key) 
                == filter.value]
    
    def evaluate_neq_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    != filter.value]
    
    def evaluate_gt_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using GREATER THAN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r'^date', filter.data_type) is not None:
            datetime_fmt = re.findall(r'^date: (.*)', filter.data_type)[0]
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [d for d in search_result.result 
                    if d.document_metadata.get(filter.key)
                        is not None
                    and datetime.strptime(d.document_metadata.get(filter.key), datetime_fmt)
                        > filter.value]
        if filter.data_type == "numeric":
            return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    > filter.value]
        
    def evaluate_lt_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using LESS THAN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r'^date', filter.data_type) is not None:
            datetime_fmt = re.findall(r'^date: (.*)', filter.data_type)[0]
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [d for d in search_result.result 
                    if d.document_metadata.get(filter.key)
                        is not None
                    and datetime.strptime(d.document_metadata.get(filter.key), datetime_fmt)
                        < filter.value]
        if filter.data_type == "numeric":
            return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    < filter.value]
        
    def evaluate_gte_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using GREATER THAN EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r'^date', filter.data_type) is not None:
            datetime_fmt = re.findall(r'^date: (.*)', filter.data_type)[0]
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [d for d in search_result.result 
                    if d.document_metadata.get(filter.key)
                        is not None
                    and datetime.strptime(d.document_metadata.get(filter.key), datetime_fmt)
                        >= filter.value]
        if filter.data_type == "numeric":
            return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    >= filter.value]
        
    def evaluate_lte_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using LESS THAN EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r'^date', filter.data_type) is not None:
            datetime_fmt = re.findall(r'^date: (.*)', filter.data_type)[0]
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [d for d in search_result.result 
                    if d.document_metadata.get(filter.key)
                        is not None
                    and datetime.strptime(d.document_metadata.get(filter.key), datetime_fmt)
                        <= filter.value]
        if filter.data_type == "numeric":
            return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and d.document_metadata.get(filter.key) 
                    <= filter.value]
    
    def evaluate_con_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using CONTAINS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and self.find_contains(filter.value, d.document_metadata.get(filter.key))]
    
    def evaluate_ncon_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using NOT CONTAINS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and not self.find_contains(filter.value, d.document_metadata.get(filter.key))]
    
    def evaluate_reg_filter(self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions):
        """
        Performs filtering using REGEX operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [d for d in search_result.result 
                if d.document_metadata.get(filter.key) 
                    is not None
                and re.search(filter.value) is not None]
    
    def evaluate_semantic_filter(self, search_result: List[MatchedDocument], domain: DomainEnum, filter: AdvancedFilterConditions):
        """
        Performs filtering using semantic search on specific metadata and entities from retrieved documents
        [Parameters]
          search_result: List[MatchedDocument]
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
    
    def find_contains(self, value, source):
        for val in value:
            if val in source.split():
                return True
        return False

    def run_search(self, query, domain, advanced_filter):
        """
        Calls query preprocessing, keyword search, and advanced filter methods
        [Parameters]
        [Returns]
          response: SemanticSearchResponse
        """
        processed_query = self.preprocess_query(query)
        search_result = self.elastic_keyword_search(processed_query, domain)
        search_result = self.evaluate_advanced_filter(search_result, domain, advanced_filter)

        return SemanticSearchResponseSchema(
            message=f"Successfully retrieved {len(search_result.result)} documents",
            result=search_result.result
        )
        
        # *tentative TODO: Transform result from last function call to response schema
