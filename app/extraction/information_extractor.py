from typing import Dict, Any

from app.extraction.general_extractor import GeneralExtractor
from app.extraction.domains.scientific.scientific_extractor import ScientificExtractor


class InformationExtractor:
    """
    InformationExtractor class is a class for extracting information from text.

    [Attributes]
        entity_extractor: EntityExtractor -> EntityExtractor class for extracting entities from text.
        metadata_extractor: MetadataExtractor -> MetadataExtractor class for extracting metadata from text.
    """

    extractor_mapping = {
        "general": GeneralExtractor,
        "scientific": ScientificExtractor,
    }

    def __init__(self, domain: str = "general") -> None:
        """
        Constructor of InformationExtractor class

        [Arguments]
            entity_extractor: EntityExtractor -> EntityExtractor class for extracting entities from text.
            metadata_extractor: MetadataExtractor -> MetadataExtractor class for extracting metadata from text.
        """
        if domain not in self.extractor_mapping:
            domain = "general"

        self.extractor = self.extractor_mapping[domain]()

    def extract(self, file: bytes) -> Dict[str, Any]:
        """
        Extract entities and metadata from text

        [Arguments]
            text: str -> Text to extract entities from
            file: IO -> File to extract metadata from
        """

        return self.extractor.extract(file)