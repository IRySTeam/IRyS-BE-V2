from app.extraction.domains.scientific import SCIENTIFIC_ENTITIES, SCIENTIFIC_METADATA

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
}

ENTITES = {
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
}

METADATA = {
    "general": [],
    "scientific": SCIENTIFIC_METADATA,
}
