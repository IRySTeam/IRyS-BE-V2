from typing import IO, Dict, Any

# from app.extraction.entity_extractor import EntityExtractor
from app.extraction.metadata_extractor import MetadataExtractor

# from app.extraction.domains.scientific import ScientificEntityExtractor
from app.extraction.domains.scientific import ScientificMetadataExtractor


class InformationExtractor:
    """
    InformationExtractor class is a class for extracting information from text.

    [Attributes]
        entity_extractor: EntityExtractor -> EntityExtractor class for extracting entities from text.
        metadata_extractor: MetadataExtractor -> MetadataExtractor class for extracting metadata from text.
    """

    domain_mapping = {
        "general": (
            # EntityExtractor,
            MetadataExtractor,
        ),
        "scientific": (
            # ScientificEntityExtractor,
            ScientificMetadataExtractor,
        ),
        # "recruitment": {
        # RecruitmentEntityExtractor,
        # RecruitmentMetadataExtractor,
        # }
    }

    def __init__(self, domain: str = "general") -> None:
        """
        Constructor of InformationExtractor class

        [Arguments]
            entity_extractor: EntityExtractor -> EntityExtractor class for extracting entities from text.
            metadata_extractor: MetadataExtractor -> MetadataExtractor class for extracting metadata from text.
        """
        if domain not in self.domain_mapping:
            domain = "general"

        # self.entity_extractor = self.domain_mapping[domain][0]()
        self.metadata_extractor = self.domain_mapping[domain][0]()

    # TODO: should the input be just the file and the text are extracted from the file
    def extract_all(self, text: str, file: IO) -> Dict[str, Any]:
        """
        Extract entities and metadata from text

        [Arguments]
            text: str -> Text to extract entities from
            file: IO -> File to extract metadata from
        """

        entities = self.extract_entities(text)
        metadata = self.extract_metadata(file)
        return {"entities": entities, "metadata": metadata}

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text

        [Arguments]
            text: str -> Text to extract entities from
        """

        # return self.entity_extractor.extract(text)
        return {}

    def extract_metadata(self, file: IO) -> Dict[str, Any]:
        """
        Extract metadata from text

        [Arguments]
            file: IO -> File to extract metadata from
        """

        return self.metadata_extractor.extract(file)
