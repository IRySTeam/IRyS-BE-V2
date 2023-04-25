import json
import magic
import mimetypes
import re
from typing import Optional, List
from binascii import a2b_base64, b2a_base64
from datetime import datetime
from fastapi import UploadFile
from tika import parser

from app.search.constants.search import DOMAIN_INDEXES
from app.search.enums.search import DomainEnum, FilterOperatorEnum
from app.search.schemas.elastic import MatchedDocument, SearchResult
from app.search.schemas.advanced_search import AdvancedFilterConditions, AdvancedSearchQuery
from app.search.schemas.search import SemanticSearchResponseSchema
from app.search.services.advanced_search import AdvancedSearchService
from app.elastic.client import ElasticsearchClient
from app.preprocess import PreprocessUtil, OCRUtil

class SearchService:
    def __init__(self, algorithm, domain, scoring):
        self.algorithm = algorithm
        self.domain = DomainEnum.GENERAL  # domain
        self.scoring = scoring

    def preprocess_query(self, query: str):
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

    def elastic_keyword_search(self, query: str, domain: DomainEnum):
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
                return AdvancedSearchService().evaluate_in_filter(search_result, filter)
            case FilterOperatorEnum.NIN:
                return AdvancedSearchService().evaluate_nin_filter(search_result, filter)
            case FilterOperatorEnum.EXI:
                return AdvancedSearchService().evaluate_exi_filter(search_result, filter)
            case FilterOperatorEnum.NEXI:
                return AdvancedSearchService().evaluate_nexi_filter(search_result, filter)
            case FilterOperatorEnum.EQ:
                return AdvancedSearchService().evaluate_eq_filter(search_result, filter)
            case FilterOperatorEnum.NEQ:
                return AdvancedSearchService().evaluate_neq_filter(search_result, filter)
            case FilterOperatorEnum.GT:
                return AdvancedSearchService().evaluate_gt_filter(search_result, filter)
            case FilterOperatorEnum.LT:
                return AdvancedSearchService().evaluate_lt_filter(search_result, filter)
            case FilterOperatorEnum.GTE:
                return AdvancedSearchService().evaluate_gte_filter(search_result, filter)
            case FilterOperatorEnum.LTE:
                return AdvancedSearchService().evaluate_lte_filter(search_result, filter)
            case FilterOperatorEnum.CON:
                return AdvancedSearchService().evaluate_con_filter(search_result, filter)
            case FilterOperatorEnum.NCON:
                return AdvancedSearchService().evaluate_ncon_filter(search_result, filter)
            case FilterOperatorEnum.REG:
                return AdvancedSearchService().evaluate_reg_filter(search_result, filter)
            case FilterOperatorEnum.SEM:
                return AdvancedSearchService().evaluate_semantic_filter(search_result, domain, filter)
            case _:
                print('No operator match found')
        return search_result
    
    def run_file_search(self, file: UploadFile, domain: DomainEnum):
        file.file.seek(0)

        processed_query = self.parsing(
            file_content_str=b2a_base64(file.file.read()).decode("utf-8"),
        )
        search_result = self.elastic_keyword_search(processed_query, domain)

        return SemanticSearchResponseSchema(
            message=f"Successfully retrieved {len(search_result.result)} documents",
            result=search_result.result
        )


    def run_search(self, query: str, domain: DomainEnum, advanced_filter: AdvancedSearchQuery):
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
    
    def parsing(self, file_content_str: str, with_ocr: bool = True):
        """
        Extracts and preprocesses text from uploaded document
        [Parameters]
            file_content_str: str -> Decoded file content in base64.
            with_ocr: bool -> Whether to OCR the document or not.
        [Returns]
            str
        """
        try:
            file_content = a2b_base64(file_content_str)
            file_text: str = parser.from_buffer(file_content)["content"]
            # TODO: Handle different file types and utilize OCR

            return " ".join(PreprocessUtil.preprocess(file_text))
        except Exception as e:
            print(e)
            raise e
        