from app.extraction.domains.recruitment.configuration import (
    RECRUITMENT_ENTITIES,
    RECRUITMENT_INFORMATION,
    RECRUITMENT_INFORMATION_NOT_FLATTENED,
)
from app.extraction.domains.scientific.configuration import (
    SCIENTIFIC_ENTITIES,
    SCIENTIFIC_INFORMATION,
    SCIENTIFIC_INFORMATION_NOT_FLATTENED,
)
from app.extraction.general_configuration import (
    GENERAL_ENTITIES,
    GENERAL_INFORMATION,
    GENERAL_INFORMATION_NOT_FLATTENED,
)

__all__ = [
    "RECRUITMENT_INFORMATION_NOT_FLATTENED",
    "SCIENTIFIC_INFORMATION_NOT_FLATTENED",
    "GENERAL_INFORMATION_NOT_FLATTENED",
]

TYPE_OPERATORS = {
    "text": [
        "equals",
        "not_equals",
        "exists",
        "not_exists",
        "in",
        "not_in",
        "regex",
        "contains",
        "not_contains",
    ],
    "semantic text": [
        "equals",
        "not_equals",
        "exists",
        "not_exists",
        "in",
        "not_in",
        "regex",
        "contains",
        "not_contains",
    ],
    "number": [
        "equals",
        "not_equals",
        "greater_than",
        "greater_than_eq",
        "less_than",
        "less_than_eq",
        "in",
        "not_in",
        "regex",
        "contains",
        "not_contains",
    ],
    "date": [
        "equals",
        "not_equals",
        "greater_than",
        "greater_than_eq",
        "less_than",
        "less_than_eq",
        "in",
        "not_in",
    ],
}

ENTITIES = {
    "general": GENERAL_ENTITIES,
    "scientific": SCIENTIFIC_ENTITIES,
    "recruitment": RECRUITMENT_ENTITIES,
}

EXTRACTED_INFORMATION = {
    "general": ENTITIES["general"] + GENERAL_INFORMATION,
    "scientific": ENTITIES["scientific"] + GENERAL_INFORMATION + SCIENTIFIC_INFORMATION,
    "recruitment": ENTITIES["recruitment"]
    + GENERAL_INFORMATION
    + RECRUITMENT_INFORMATION,
}
