# from app.extraction.domains.paper.entities import PaperEntityExtractor
from app.extraction.domains.scientific.metadata import ScientificMetadataExtractor
from app.extraction.domains.scientific.configuration import (
    SCIENTIFIC_ENTITIES,
    SCIENTIFIC_METADATA,
)

__all__ = [
    # "ScientificEntityExtractor"
    "ScientificMetadataExtractor",
    "SCIENTIFIC_ENTITIES",
    "SCIENTIFIC_METADATA",
]
