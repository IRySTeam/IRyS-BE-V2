from copy import deepcopy

# =============================================================================
# Base configuration for Elasticsearch.
# =============================================================================
BASE_ELASTICSEARCH_INDEX_MAPPINGS = {
    "dynamic": "true",
    "_source": {"enabled": "true"},
    "properties": {
        "document_id": {"type": "integer"},
        "title": {"type": "text"},
        "raw_text": {"type": "text"},
        "processed_text": {"type": "text"},
        "text_vector": {"type": "dense_vector", "dims": 768},
        "document_label": {"type": "text"},
        "document_metadata": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "text"},
                        "results": {
                            "type": "object",
                            "properties": {
                                "entity_group": {"type": "text"},
                                "score": {"type": "float"},
                                "word": {"type": "text"},
                                "start": {"type": "integer"},
                                "end": {"type": "integer"},
                            },
                        },
                        "entities": {
                            # List of text.
                            "type": "text",
                            # Use the keyword field type to enable exact match, sorting, and aggregations.
                            "fields": {"keyword": {"type": "keyword"}},
                        },
                    },
                }
            },
        },
    },
}


# =============================================================================
# General domain configuration for Elasticsearch.
# =============================================================================
GENERAL_ELASTICSEARCH_INDEX_NAME = "general-msmarco"

# TODO: Redefine this settings.
GENERAL_ELASTICSEARCH_INDEX_SETTINGS = {"number_of_shards": 2, "number_of_replicas": 1}

GENERAL_ELASTICSEARCH_INDEX_INFORMATION = {
    "mimetype": {"type": "text"},
    "extension": {"type": "text"},
    "size": {"type": "integer"},
    "dates": {"type": "text"},
}

GENERAL_ELASTICSEARCH_INDEX_MAPPINGS = deepcopy(BASE_ELASTICSEARCH_INDEX_MAPPINGS)
GENERAL_ELASTICSEARCH_INDEX_MAPPINGS["properties"]["document_metadata"][
    "properties"
].update(GENERAL_ELASTICSEARCH_INDEX_INFORMATION)


# =============================================================================
# Recruitment domain configuration for Elasticsearch.
# =============================================================================
RECRUITMENT_ELASTICSEARCH_INDEX_NAME = "recruitment-msmarco"

# TODO: Redefine this settings.
RECRUITMENT_ELASTICSEARCH_INDEX_SETTINGS = {
    "number_of_shards": 2,
    "number_of_replicas": 1,
}

RECRUITMENT_ELASTICSEARCH_INDEX_INFORMATION = {
    "COMPANY": {"type": "text"},
    "DEGREE": {"type": "text"},
    "INSTITUTION": {"type": "text"},
    "LOC": {"type": "text"},
    "ORG": {"type": "text"},
    "PER": {"type": "text"},
    "ROLE": {"type": "text"},
    "SKILL": {"type": "text"},
    "name": {"type": "text"},
    "email": {"type": "text"},
    "skills": {"type": "text"},
    "experiences": {
        "type": "object",
        "properties": {
            "job_title": {"type": "text"},
            "company": {"type": "text"},
            "start_date": {"type": "text"},
            "end_date": {"type": "text"},
            "description": {"type": "text"},
        },
    },
    "education": {
        "type": "object",
        "properties": {
            "institution": {"type": "text"},
            "degree": {"type": "text"},
            "start_date": {"type": "text"},
            "end_date": {"type": "text"},
            "description": {"type": "text"},
        },
    },
    "projects": {
        "type": "object",
        "properties": {
            "title": {"type": "text"},
            "description": {"type": "text"},
        },
    },
    "certifications": {
        "type": "object",
        "properties": {
            "title": {"type": "text"},
            "description": {"type": "text"},
        },
    },
    "experiences_job_titles": {"type": "text"},
    "experiences_companies": {"type": "text"},
    "experiences_descriptions": {
        "type": "object",
        "properties": {
            "text": {"type": "text"},
            "text_vector": {"type": "dense_vector", "dims": 768},
        },
    },
    "education_insitutions": {"type": "text"},
    "education_degrees": {"type": "text"},
    "education_descriptions": {
        "type": "object",
        "properties": {
            "text": {"type": "text"},
            "text_vector": {"type": "dense_vector", "dims": 768},
        },
    },
    "projects_titles": {"type": "text"},
    "projects_descriptions": {
        "type": "object",
        "properties": {
            "text": {"type": "text"},
            "text_vector": {"type": "dense_vector", "dims": 768},
        },
    },
    "certifications_titles": {"type": "text"},
    "certifications_descriptions": {
        "type": "object",
        "properties": {
            "text": {"type": "text"},
            "text_vector": {"type": "dense_vector", "dims": 768},
        },
    },
}

RECRUITMENT_ELASTICSEARCH_INDEX_MAPPINGS = deepcopy(BASE_ELASTICSEARCH_INDEX_MAPPINGS)
RECRUITMENT_ELASTICSEARCH_INDEX_MAPPINGS["properties"]["document_metadata"][
    "properties"
].update(GENERAL_ELASTICSEARCH_INDEX_INFORMATION)
RECRUITMENT_ELASTICSEARCH_INDEX_MAPPINGS["properties"]["document_metadata"][
    "properties"
].update(RECRUITMENT_ELASTICSEARCH_INDEX_INFORMATION)

# =============================================================================
# Scientific domain configuration for Elasticsearch.
# =============================================================================
SCIENTIFIC_ELASTICSEARCH_INDEX_NAME = "scientific-msmarco"

# TODO: Redefine this settings.
SCIENTIFIC_ELASTICSEARCH_INDEX_SETTINGS = {
    "number_of_shards": 2,
    "number_of_replicas": 1,
}

SCIENTIFIC_ELASTICSEARCH_INDEX_CONFIGURATION = {
    "CONCEPT": {"type": "text"},
    "INSTITUTION": {"type": "text"},
    "LOC": {"type": "text"},
    "METRICS": {"type": "text"},
    "ORG": {"type": "text"},
    "PER": {"type": "text"},
    "TOOLS": {"type": "text"},
    "authors": {"type": "text"},
    "affiliations": {"type": "text"},
    "abstract": {
        "type": "object",
        "properties": {
            "text_vector": {"type": "dense_vector", "dims": 768},
            "text": {"type": "text"},
        },
    },
    "title": {
        "type": "object",
        "properties": {
            "text_vector": {"type": "dense_vector", "dims": 768},
            "text": {"type": "text"},
        },
    },
    "keywords": {"type": "text"},
    "references": {"type": "text"},
}

SCIENTIFIC_ELASTICSEARCH_INDEX_MAPPINGS = deepcopy(BASE_ELASTICSEARCH_INDEX_MAPPINGS)
SCIENTIFIC_ELASTICSEARCH_INDEX_MAPPINGS["properties"]["document_metadata"][
    "properties"
].update(GENERAL_ELASTICSEARCH_INDEX_INFORMATION)
SCIENTIFIC_ELASTICSEARCH_INDEX_MAPPINGS["properties"]["document_metadata"][
    "properties"
].update(SCIENTIFIC_ELASTICSEARCH_INDEX_CONFIGURATION)
