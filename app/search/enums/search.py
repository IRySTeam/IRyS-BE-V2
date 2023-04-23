from enum import Enum

class ScoringAlgorithmEnum(str, Enum):
    COSINE_SIMILARITY = 'COSINE_SIMILARITY'
    DOT_PRODUCT = 'DOT_PRODUCT'
    OKAPI_BM = 'OKAPI_BM'

class DomainEnum(str, Enum):
    GENERAL = 'GENERAL'
    RECRUITMENT = 'RECRUITMENT'
    SCIENTIFIC = 'SCIENTIFIC'

class FilterOperatorEnum(str, Enum):
    IN = 'IN'
    NIN = 'NOT IN'
    EXI = 'EXISTS'
    NEXI = 'NOT EXISTS'
    EQ = 'EQUAL'
    NEQ = 'NOT EQUAL'
    GT = 'GREATER THAN'
    LT = 'LESS THAN'
    GTE = 'GREATER THAN EQUAL'
    LTE = 'LESS THAN EQUAL'    
    CON = 'CONTAINS'
    NCON = 'NOT CONTAINS'
    REG = 'REGEX'
    SEM = 'SEMANTIC SEARCH'
