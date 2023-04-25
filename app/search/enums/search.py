from enum import Enum


class SearchAlgorithmEnum(Enum):
    SYNTAX = 1
    SEMANTIC = 2


class ScoringAlgorithmEnum(Enum):
    COSINE_SIMILARITY = 1
    OTHER = 2


class DomainEnum(Enum):
    GENERAL = 1
    RECRUITMENT = 2
    SCIENTIFIC = 3


class FilterOperatorEnum(Enum):
    IN = 1
    NOT_IN = 2
    EXIST = 3
    NOT_EXIST = 4
    EQUAL = 5
    NOT_EQUAL = 6
    GREATER = 7
    SMALLER = 8
    GREATER_EQUAL = 9
    SMALLER_EQUAL = 10
