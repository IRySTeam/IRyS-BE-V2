from app.extraction.domains.recruitment import (
    RECRUITMENT_ENTITIES,
    RECRUITMENT_INFORMATION,
)
from app.extraction.domains.scientific import (
    SCIENTIFIC_ENTITIES,
    SCIENTIFIC_INFORMATION,
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
    "general": [
        {
            "name": "LOC",
            "type": "text",
        },
        {
            "name": "MISC",
            "type": "text",
        },
        {
            "name": "ORG",
            "type": "text",
        },
        {
            "name": "PER",
            "type": "text",
        },
    ],
    "scientific": SCIENTIFIC_ENTITIES,
    "recruitment": RECRUITMENT_ENTITIES,
}

GENERAL_INFORMATION = [
    {
        "name": "mimetype",
        "type": "text",
    },
    {
        "name": "extension",
        "type": "text",
    },
    {
        "name": "size",
        "type": "number",
    },
]

EXTRACTED_INFORMATION = {
    "general": ENTITIES["general"] + GENERAL_INFORMATION,
    "scientific": ENTITIES["scientific"] + GENERAL_INFORMATION + SCIENTIFIC_INFORMATION,
    "recruitment": ENTITIES["recruitment"]
    + GENERAL_INFORMATION
    + RECRUITMENT_INFORMATION,
}
