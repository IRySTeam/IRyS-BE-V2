from app.extraction.domains.scientific import (
    SCIENTIFIC_ENTITIES,
    SCIENTIFIC_INFORMATION,
)
from app.extraction.domains.recruitment import (
    RECRUITMENT_ENTITIES,
    RECRUITMENT_INFORMATION,
)

TYPE_OPERATORS = {
    "text": [
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
        "less_than",
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
    "general": {
        "entities": ENTITIES["general"],
        "information": GENERAL_INFORMATION,
    },
    "scientific": {
        "entities": ENTITIES["scientific"],
        "information": GENERAL_INFORMATION + SCIENTIFIC_INFORMATION,
    },
    "recruitment": {
        "entities": ENTITIES["recruitment"],
        "information": GENERAL_INFORMATION + RECRUITMENT_INFORMATION,
    },
}
