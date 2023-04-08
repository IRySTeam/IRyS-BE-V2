GENERAL_ELASTICSEARCH_INDEX_NAME = "general-0001"

# TODO: Redefine this settings.
GENERAL_ELASTICSEARCH_INDEX_SETTINGS = {"number_of_shards": 2, "number_of_replicas": 1}

# TODO: Redefine this mapping.
GENERAL_ELASTICSEARCH_INDEX_MAPPINGS = {
    "dynamic": "true",
    "_source": {"enabled": "true"},
    "properties": {
        "title": {"type": "text"},
        "raw_text": {"type": "text"},
        "processed_text": {"type": "text"},
        "text_vector": {"type": "dense_vector", "dims": 768},
    },
}

RECRUITMENT_ELASTICSEARCH_INDEX_NAME = "recruitment-0001"

# TODO: Redefine this settings.
RECRUITMENT_ELASTICSEARCH_INDEX_SETTINGS = {
    "number_of_shards": 2,
    "number_of_replicas": 1,
}

# TODO: Redefine this mapping.
RECRUITMENT_ELASTICSEARCH_INDEX_MAPPINGS = {
    "dynamic": "true",
    "_source": {"enabled": "true"},
    "properties": {
        "title": {"type": "text"},
        "text": {"type": "text"},
        "text_vector": {"type": "dense_vector", "dims": 768},
    },
}

SCIENTIFIC_ELASTICSEARCH_INDEX_NAME = "scientific-0001"

# TODO: Redefine this settings.
SCIENTIFIC_ELASTICSEARCH_INDEX_SETTINGS = {
    "number_of_shards": 2,
    "number_of_replicas": 1,
}

# TODO: Redefine this mapping.
SCIENTIFIC_ELASTICSEARCH_INDEX_MAPPINGS = {
    "dynamic": "true",
    "_source": {"enabled": "true"},
    "properties": {
        "title": {"type": "text"},
        "text": {"type": "text"},
        "text_vector": {"type": "dense_vector", "dims": 768},
    },
}
