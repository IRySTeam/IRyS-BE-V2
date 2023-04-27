import mimetypes
from typing import Any, Dict

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

        mimetype = magic.from_buffer(file, mime=True)
        extension = mimetypes.guess_extension(mimetype)
        size = len(file)

        file_text: str = parser.from_buffer(file)["content"].strip()

        entities = self.extract_entities(file_text)

        flattened_entities = {
            entity["name"]: [
                entity_res["word"]
                for entity_res in entities.results
                if entity_res["entity_group"] == entity["name"]
            ]
            for entity in self.entity_list
        }

        result = {
            "mimetype": mimetype,
            "extension": extension,
            "size": size,
            "entities": entities,
        }
        result.update(flattened_entities)

        return result

    def extract_entities(self, text: str) -> NERResult:
        """
        Extract entities from text

        [Arguments]
            text: str -> Text to extract entities from
        [Returns]
            List[Dict[str, Any]] -> List of entities
        """

        preprocessed = self.preprocess(text)
        ner_result = self.pipeline(preprocessed)
        for ner in ner_result:
            ner["score"] = ner["score"].item()
        return NERResult(text, ner_result)
