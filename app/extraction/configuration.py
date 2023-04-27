from app.extraction.domains.recruitment.configuration import (
    RECRUITMENT_ENTITIES,
    RECRUITMENT_INFORMATION,
)
from app.extraction.domains.scientific.configuration import (
    SCIENTIFIC_ENTITIES,
    SCIENTIFIC_INFORMATION,
)
from app.extraction.general_configuration import (
    GENERAL_ENTITIES,
    GENERAL_INFORMATION,
)

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
        "contains",
        "not_contains",
        "starts_with",
        "ends_with",
        "equals",
        "regex",
        "in",
        "not_in",
    ],
    "list": [
        "contains",
        "not_contains",
        "equals",
        "in",
        "not_in",
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
