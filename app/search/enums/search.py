from enum import Enum


class ScoringAlgorithmEnum(str, Enum):
    COSINE_SIMILARITY = "COSINE_SIMILARITY"
    DOT_PRODUCT = "DOT_PRODUCT"
    OKAPI_BM = "OKAPI_BM"


class DomainEnum(str, Enum):
    GENERAL = "general"
    RECRUITMENT = "recruitment"
    SCIENTIFIC = "scientific"


class FilterOperatorEnum(str, Enum):
    IN = "in"
    NIN = "not_in"
    EXI = "exists"
    NEXI = "not_exists"
    EQ = "equals"
    NEQ = "not_equals"
    GT = "greater_than"
    LT = "less_than"
    GTE = "greater_than_eq"
    LTE = "less_than_eq"
    CON = "contains"
    NCON = "not_contains"
    REG = "regex"
    SEM = "semantic_search"
