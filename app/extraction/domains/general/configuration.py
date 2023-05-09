GENERAL_ENTITIES = [
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
]

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
    {
        "name": "dates",
        "type": "date",
    },
]

GENERAL_INFORMATION_NOT_FLATTENED = [
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
    {
        "name": "dates",
        "type": "date",
    },
]

NER_MODEL = "dslim/bert-base-NER"
