import re
from typing import List
from datetime import datetime

from app.search.enums.search import DomainEnum
from app.search.schemas.elastic import MatchedDocument
from app.search.schemas.advanced_search import AdvancedFilterConditions
from app.elastic.client import ElasticsearchClient

class AdvancedSearchService:
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