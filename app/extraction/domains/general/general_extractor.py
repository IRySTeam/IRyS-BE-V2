import os

from transformers import pipeline

from app.extraction.base_extractor import BaseExtractor
from app.extraction.domains.general.configuration import (
    GENERAL_ENTITIES,
    NER_MODEL,
)
from app.extraction.ner_result import NERResult

dir_path = os.path.dirname(os.path.realpath(__file__))


class GeneralExtractor(BaseExtractor):
    """
    GeneralExtractor class is a base class for general domain named entity recognition
    and can be extended for more specific domain.

    [Attributes]
    pipeline: Pipeline -> Huggingface NER pipeline.
    """

    entity_list = GENERAL_ENTITIES

    def __init__(self):
        """
        Constructor of GeneralExtractor class
        """
        print("Dalam GeneralExtractor")
        self.pipeline = pipeline(
            "ner",
            model=NER_MODEL,
            aggregation_strategy="first",
        )

        print("Dalam GeneralExtractor 2")

    def preprocess(self, text: str) -> str:
        """
        Preprocess text for general domain

        [Arguments]
            text: str -> Text to preprocess
        [Returns]
            str -> Preprocessed text
        """

        return text

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
