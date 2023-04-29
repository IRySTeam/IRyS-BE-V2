import datetime
import mimetypes
from typing import Any, Dict, List

import dateparser.search
import magic
from tika import parser
from transformers import pipeline

from app.extraction.general_configuration import GENERAL_ENTITIES
from app.extraction.ner_result import NERResult


class GeneralExtractor:
    """
    GeneralExtractor class is a base class for general domain named entity recognition
    and can be extended for more specific domain.

    [Attributes]
    pipeline: Pipeline -> Huggingface NER pipeline.
    """

    def __init__(self):
        """
        Constructor of GeneralExtractor class
        """

        self.pipeline = pipeline(
            "ner", model="dslim/bert-base-NER", aggregation_strategy="first"
        )
        self.entity_list = GENERAL_ENTITIES

    def preprocess(self, text: str) -> str:
        """
        Preprocess text for general domain

        [Arguments]
            text: str -> Text to preprocess
        [Returns]
            str -> Preprocessed text
        """

        return text

    def extract(self, file: bytes) -> Dict[str, Any]:
        """
        Extract entities and information from file

        [Arguments]
            file: bytes -> File to extract metadata from
        [Returns]
            Dict[str, Any] -> Dictionary containing extracted information and entities
        """

        # Extract general information
        result = self.extract_general_information(file)

        file_text: str = parser.from_buffer(file)["content"].strip()

        entities = self.extract_entities(file_text)

        flattened_entities = self.flatten_entities(entities)

        result.update({"entities": entities})
        result.update(flattened_entities)

        # Extract dates
        dates = self.__extract_dates(file_text)
        result.update({"dates": dates})

        return result

    def extract_entities(self, text: str) -> NERResult:
        """
        Extract entities from text

        [Arguments]
            text: str -> Text to extract entities from
        [Returns]
            NERResult -> Named entity recognition result
        """

        preprocessed = self.preprocess(text)
        ner_result = self.pipeline(preprocessed)
        for ner in ner_result:
            ner["score"] = ner["score"].item()
        return NERResult(text, ner_result)

    def extract_general_information(self, file: bytes) -> Dict[str, Any]:
        """
        Extract general information from file

        [Arguments]
            file: bytes -> File to extract information from
        [Returns]
            Dict[str, Any] -> Dictionary containing extracted information
        """

        mimetype = magic.from_buffer(file, mime=True)
        extension = mimetypes.guess_extension(mimetype)
        size = len(file)

        return {
            "mimetype": mimetype,
            "extension": extension,
            "size": size,
        }

    def flatten_entities(self, entities: NERResult) -> Dict[str, Any]:
        """
        Flatten entities to a dictionary

        [Arguments]
            entities: List[Dict[str, Any]] -> List of entities
        [Returns]
            Dict[str, Any] -> Dictionary of entities
        """

        flattened_entities = {
            entity["name"]: [
                entity_res["word"]
                for entity_res in entities.results
                if entity_res["entity_group"] == entity["name"]
            ]
            for entity in self.entity_list
        }

        return flattened_entities

    def __extract_dates(self, text: str) -> List[datetime.date]:
        """
        Extract dates from text

        [Arguments]
            text: str -> Text to extract dates from
        [Returns]
            List[datetime.date] -> List of dates
        """

        dates = dateparser.search.search_dates(
            text, languages=["en"], settings={"PREFER_DAY_OF_MONTH": "first"}
        )
        if dates is None:
            return []
        return [date[1].date() for date in dates]
