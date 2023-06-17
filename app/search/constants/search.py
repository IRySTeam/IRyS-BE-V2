from app.search.enums.search import DomainEnum

DOMAIN_INDEXES = {
    DomainEnum.GENERAL: "general-msmarco",
    DomainEnum.RECRUITMENT: "recruitment_index",
    DomainEnum.SCIENTIFIC: "scientific_index",
}

FIELD_WEIGHTS = {
    DomainEnum.RECRUITMENT: [
        'preprocessed_text^1', 
        'document_metadata.COMPANY^1', 
        'document_metadata.DEGREE^1',
        'document_metadata.INSTITUTION^1',
        'document_metadata.LOC^2',
        'document_metadata.ORG^1',
        'document_metadata.PER^2',
        'document_metadata.ROLE^6',
        'document_metadata.SKILL^3',
        'document_metadata.name^2',
        'document_metadata.skills^2',
        'document_metadata.experiences_job_titles^1',
        'document_metadata.experiences_companies^1',
        'document_metadata.experiences_descriptions^1',
        'document_metadata.education_institutions^1',
        'document_metadata.education_degrees^1',
        'document_metadata.education_descriptions^1',
        'document_metadata.projects_descriptions^1',
        'document_metadata.certifications_titles^1',
        'document_metadata.certifications_descriptions^1'
    ],
    DomainEnum.SCIENTIFIC: [
        'preprocessed_text^1', 
        'document_metadata.CONCEPT^2', 
        'document_metadata.INSTITUTION^1', 
        'document_metadata.LOC^1', 
        'document_metadata.METRICS^1', 
        'document_metadata.ORG^1', 
        'document_metadata.PER^3', 
        'document_metadata.TOOLS^1', 
        'document_metadata.title^1', 
        'document_metadata.authors^3', 
        'document_metadata.affiliations^1', 
        'document_metadata.abstract^1', 
        'document_metadata.keywords^5', 
        'document_metadata.references^1', 
    ],
    DomainEnum.GENERAL: [
        'preprocessed_text^3', 
        'document_metadata.LOC^1',
        'document_metadata.MISC^1',
        'document_metadata.ORG^2',
        'document_metadata.PER^2',
        'document_metadata.title^2', 
    ]   
}