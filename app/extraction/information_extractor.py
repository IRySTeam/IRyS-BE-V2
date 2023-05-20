from typing import Any, Dict, Union

from app.extraction.domains.general import GeneralExtractor
from app.extraction.domains.recruitment import RecruitmentExtractor
from app.extraction.domains.scientific import ScientificExtractor


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
        "recruitment": RecruitmentExtractor,
    }

    def __init__(self, domain: str = "general") -> None:
        """
        Constructor of InformationExtractor class

        [Arguments]
            entity_extractor: EntityExtractor -> EntityExtractor class for extracting entities from text.
            metadata_extractor: MetadataExtractor -> MetadataExtractor class for extracting metadata from text.
        """
        if domain not in self.extractor_mapping:
            print("Dalam if ")
            domain = "general"

        print("Dalam 2")
        self.extractor: Union[
            GeneralExtractor, ScientificExtractor, RecruitmentExtractor
        ] = self.extractor_mapping[domain]()

        print("Dalam 3")

    def extract(
        self,
        file: bytes,
        file_text: str = None,
    ) -> Dict[str, Any]:
        """
        Extract entities and metadata from text

        [Arguments]
            file: bytes -> File to extract metadata from
            file_text: str -> Text of file to extract entities from (optional), used when
                file is scanned PDF
        """

        return self.extractor.extract(file, file_text)
