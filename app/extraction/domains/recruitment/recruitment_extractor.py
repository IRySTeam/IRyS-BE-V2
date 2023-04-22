import os
import io
import re
import fitz
import nltk
import string
import pickle
import pathlib
import pandas as pd

from transformers import pipeline
from typing import List, Union, Dict, Any
from collections import defaultdict
from app.extraction.general_extractor import GeneralExtractor

from app.extraction.ner_result import NERResult

dir_path = os.path.dirname(os.path.realpath(__file__))


class RecruitmentExtractor(GeneralExtractor):
    """
    RecruitmentExtractor class is a class for extracting information from scientific text.
    """

    def __init__(self):
        """
        Constructor of RecruitmentExtractor class
        """

        self.pipeline = pipeline(
            "ner", model="topmas/IRyS-NER-Recruitment", aggregation_strategy="first"
        )

    def preprocess(self, text: str) -> str:
        """
        Preprocess text for recruitment domain

        [Arguments]
            text: str -> Text to preprocess
        """

        return text.replace("\n", " ")

    def extract(self, file: bytes) -> Dict[str, Any]:
        """
        Extract information from a paper file

        [Arguments]
            file: bytes -> File bytes to extract information from
        [Returns]
            Dict -> Dictionary containing extracted information
        """

        result = super().extract(file)

        # TODO: Extract information specific to recruitment domain

        return result
