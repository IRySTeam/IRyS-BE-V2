import re
from datetime import datetime
from typing import List

from app.search.constants.search import FIELD_WEIGHTS
from app.elastic.client import ElasticsearchClient
from app.search.enums.search import DomainEnum
from app.search.schemas.advanced_search import AdvancedFilterConditions
from app.search.schemas.elastic import MatchedDocument, SearchResult
from app.preprocess.preprocess import PreprocessUtil
from app.search.services.text_encoding import TextEncodingService


class AdvancedSearchService:

    def __init__(self, model: TextEncodingService = None):
        self.model = model

    def evaluate_in_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using IN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and self.any_intersection(filter.value, d.document_metadata.get(filter.key))
        ]

    def evaluate_nin_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using NOT IN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and not self.any_intersection(
                filter.value, d.document_metadata.get(filter.key)
            )
        ]

    def evaluate_exi_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using EXISTS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and bool(d.document_metadata.get(filter.key))
        ]

    def evaluate_nexi_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using NOT EXISTS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            or not bool(d.document_metadata.get(filter.key))
        ]

    def evaluate_eq_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if self.eval_basic(filter.value, d.document_metadata.get(filter.key), "==")
        ]

    def evaluate_neq_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using NOT EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and not self.eval_basic(
                filter.value, d.document_metadata.get(filter.key), "=="
            )
        ]

    def evaluate_gt_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using GREATER THAN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r"^date", filter.data_type) is not None:
            # datetime_fmt = re.findall(r"^date: (.*)", filter.data_type)[0]
            datetime_fmt = "%Y-%m-%d"
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value,
                    [
                        datetime.strptime(x, datetime_fmt) 
                        for x in d.document_metadata.get(filter.key)
                    ],
                    ">",
                )
            ]
        if filter.data_type == "number":
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value, d.document_metadata.get(filter.key), ">"
                )
            ]
        return []

    def evaluate_lt_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using LESS THAN operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r"^date", filter.data_type) is not None:
            # datetime_fmt = re.findall(r"^date: (.*)", filter.data_type)[0]
            datetime_fmt = "%Y-%m-%d"
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value,
                    [
                        datetime.strptime(x, datetime_fmt) 
                        for x in d.document_metadata.get(filter.key)
                    ],
                    "<",
                )
            ]
        if filter.data_type == "number":
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value, d.document_metadata.get(filter.key), "<"
                )
            ]
        return []

    def evaluate_gte_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using GREATER THAN EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r"^date", filter.data_type) is not None:
            # datetime_fmt = re.findall(r"^date: (.*)", filter.data_type)[0]
            datetime_fmt = "%Y-%m-%d"
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value,
                    [
                        datetime.strptime(x, datetime_fmt) 
                        for x in d.document_metadata.get(filter.key)
                    ],                    
                    ">=",
                )
            ]
        if filter.data_type == "number":
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value, d.document_metadata.get(filter.key), ">="
                )
            ]
        return []

    def evaluate_lte_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using LESS THAN EQUAL operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        if re.search(r"^date", filter.data_type) is not None:
            # datetime_fmt = re.findall(r"^date: (.*)", filter.data_type)[0]
            datetime_fmt = "%Y-%m-%d"
            filter.value = datetime.strptime(filter.value, datetime_fmt)
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value,
                    [
                        datetime.strptime(x, datetime_fmt) 
                        for x in d.document_metadata.get(filter.key)
                    ],
                    "<=",
                )
            ]
        if filter.data_type == "number":
            return [
                d
                for d in search_result.result
                if d.document_metadata.get(filter.key) is not None
                and self.eval_basic(
                    filter.value, d.document_metadata.get(filter.key), "<="
                )
            ]
        return []

    def evaluate_con_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using CONTAINS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and self.find_contains(filter.value, d.document_metadata.get(filter.key))
        ]

    def evaluate_ncon_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using NOT CONTAINS operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and not self.find_contains(
                filter.value, d.document_metadata.get(filter.key)
            )
        ]

    def evaluate_reg_filter(
        self, search_result: List[MatchedDocument], filter: AdvancedFilterConditions
    ):
        """
        Performs filtering using REGEX operator
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        return [
            d
            for d in search_result.result
            if d.document_metadata.get(filter.key) is not None
            and self.eval_regex(filter.value, d.document_metadata.get(filter.key))
        ]

    def evaluate_semantic_filter(
        self,
        search_result: List[MatchedDocument],
        domain: DomainEnum,
        filter: AdvancedFilterConditions,
    ):
        """
        Performs filtering using semantic search on specific metadata and entities from retrieved documents
        [Parameters]
          search_result: List[MatchedDocument]
          filter: SemanticFilterConditions
        [Returns]
          MatchedDocument
        """
        print("Flag 1")
        data = ElasticsearchClient().search_semantic(
            query=filter.value,
            index=f"{domain.value}-0001",
            size=filter.top_n,
            source=["document_id", "title", "preprocessed_text", "document_metadata"],
            emb_vector=f'document_metadata.{filter.key}.text_vector',
            doc_ids=[x.doc_id for x in search_result.result],
            fields=[f'document_metadata.{filter.key}.text^3'],
            model=self.model
        )
        return self.normalize_search_result(data, filter.score_threshold).result
    
    def preprocess_filter(self, value, source):
        pu = PreprocessUtil()
        
        clean_value = value
        clean_source = source
        
        # Preprocess value
        if type(value) == str:
            clean_value = ' '.join(pu.preprocess(value))
        elif type(value) == list:
            clean_value = [' '.join(pu.preprocess(x)) for x in value]

        # Preprocess source
        if type(source) == str:
            clean_source = ' '.join(pu.preprocess(source))
        elif type(source) == list:
            clean_source = [' '.join(pu.preprocess(x)) for x in source]
        elif type(source) == dict:
            clean_source = [' '.join(pu.preprocess(source.get('text')))]
        
        return clean_value, clean_source

    def generalize_type(self, value, source):
        if type(value) != list and type(value) != dict:
            value = [value]
        if (type(source) != list) and (type(source) != dict):
            source = [source]
        elif type(source) == dict:
            source = source.get("text")
        return value, source

    def find_contains(self, value, source):
        value, source = self.preprocess_filter(value, source)
        value, source = self.generalize_type(value, source)
        for val in value:
            for source_val in source:
                if re.search(f".*{val}.*", source_val, re.IGNORECASE) is not None:
                    return True
        return False

    def eval_basic(self, value, source, op):
        value, source = self.generalize_type(value, source)
        if value is None or source is None:
            return False
        search_val = value[0]
        for source_val in source:
            if self.comparator_map(op, source_val, search_val):
                return True
        return False

    def comparator_map(self, operator_str, a, b):
        match operator_str:
            case "==":
                return a == b
            case "!=":
                return a != b
            case ">":
                return a > b
            case "<":
                return a < b
            case ">=":
                return a >= b
            case "<=":
                return a <= b
            case _:
                print("No comparator match found")
        return

    def eval_regex(self, value, source):
        value, source = self.generalize_type(value, source)
        search_term = value[0]
        for source_val in source:
            if re.search(search_term, source_val, re.IGNORECASE) is not None:
                return True
        return False

    def any_intersection(self, value, source):
        value, source = self.preprocess_filter(value, source)
        value, source = self.generalize_type(value, source)
        intersection = [x for x in value if x in source]
        return bool(intersection)
    
    def normalize_search_result(self, data, min_score=1):
        search_result = SearchResult(result=[])
        for hit in data["hits"]["hits"]:
            matched_document = MatchedDocument(
                doc_id=hit["_source"]["document_id"],
                id=hit["_id"],
                score=hit["_score"],
                title=hit["_source"]["title"],
                preprocessed_text=hit["_source"]["preprocessed_text"],
                document_metadata=hit["_source"]["document_metadata"],
            )
            if (matched_document.score >= min_score):
                search_result.result.append(matched_document)
        return search_result
