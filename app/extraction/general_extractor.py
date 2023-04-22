import mimetypes
import magic
from tika import parser

# from transformers import pipeline
from typing import List, Dict, Any

# from app.extraction.ner_result import NERResult


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

        # self.pipeline = pipeline(
        #     "ner", model="dslim/bert-base-NER", aggregation_strategy="first"
        # )

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

        # entities = self.extract_entities(file_text)

        return {
            "mimetype": mimetype,
            "extension": extension,
            "size": size,
            # "entities": entities
        }

    # def extract_entities(self, text: str) -> List[Dict[str, Any]]:
    #     """
    #     Extract entities from text

    #     [Arguments]
    #         text: str -> Text to extract entities from
    #     [Returns]
    #         List[Dict[str, Any]] -> List of entities
    #     """

    #     preprocessed = self.preprocess(text)
    #     ner_result = self.pipeline(preprocessed)
    #     for ner in ner_result:
    #         ner["score"] = ner["score"].item()
    #     return NERResult(text, ner_result)
