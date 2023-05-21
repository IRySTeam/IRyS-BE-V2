import abc
import datetime
import mimetypes
from typing import Any, Dict, List

import dateparser.search
import magic
from tika import parser

from app.extraction.converter import Converter
from app.extraction.ner_result import NERResult


class BaseExtractor(abc.ABC):
    file_converter = Converter()

    @property
    @abc.abstractmethod
    def entity_list(self):
        pass

    def extract(
        self,
        file: bytes,
        file_text: str = None,
    ) -> Dict[str, Any]:
        """
        Extract entities and information from file

        [Arguments]
            file: bytes -> File to extract metadata from
            file_text: str -> Text of file to extract entities from (optional), used when
                file is scanned PDF
        [Returns]
            Dict[str, Any] -> Dictionary containing extracted information and entities
        """
        file_text = file_text or parser.from_buffer(file)["content"].strip()

        # Extract general information
        result = self.extract_general_information(file, file_text)

        entities = self.extract_entities(file_text)

        flattened_entities = self.flatten_entities(entities)

        result.update({"entities": entities.to_dict()})
        result.update(flattened_entities)

        return result

    def extract_general_information(
        self, file: bytes, file_text: str = None
    ) -> Dict[str, Any]:
        """
        Extract general information from file

        [Arguments]
            file: bytes -> File to extract information from
            file_text: str -> Text of file
        [Returns]
            Dict[str, Any] -> Dictionary containing extracted information
        """

        mimetype = magic.from_buffer(file, mime=True)
        extension = mimetypes.guess_extension(mimetype)
        size = len(file)

        # Extract dates
        if file_text is None:
            file_text: str = parser.from_buffer(file)["content"].strip()
        dates = self.__extract_dates(file_text)
        converted_dates = [date.strftime("%Y-%m-%d") for date in dates]

        # Manually convert three digit years to four digit years
        def convert_year(date: str) -> str:
            date = date.split("-")
            year = date[0]
            if len(year) != 4:
                year = year.zfill(4)
            return "-".join([year, date[1], date[2]])

        converted_dates = [convert_year(date) for date in converted_dates]

        return {
            "mimetype": mimetype,
            "extension": extension,
            "size": size,
            "dates": converted_dates,
        }

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
        return list(set([date[1].date() for date in dates]))

    @abc.abstractmethod
    def extract_entities(self, text: str) -> NERResult:
        pass

    def flatten_entities(self, entities: NERResult) -> Dict[str, Any]:
        """
        Flatten entities to a dictionary

        [Arguments]
            entities: List[Dict[str, Any]] -> List of entities
        [Returns]
            Dict[str, Any] -> Dictionary of entities
        """

        flattened_entities = {
            entity["name"]: list(
                set(
                    [
                        entity_res["word"].strip().strip("\n").strip()
                        for entity_res in entities.results
                        if entity_res["entity_group"] == entity["name"]
                    ]
                )
            )
            for entity in self.entity_list
        }

        return flattened_entities
