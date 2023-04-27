import os
import pickle
import re
import string
from collections import defaultdict
from typing import Any, Dict, List, Union

import fitz
import nltk
import pandas as pd
from transformers import pipeline

from app.extraction.general_extractor import GeneralExtractor
from app.extraction.ner_result import NERResult

dir_path = os.path.dirname(os.path.realpath(__file__))


class ScientificExtractor(GeneralExtractor):
    """
    ScientificExtractor class is a class for extracting information from scientific text.
    """

    author_classifier = pickle.load(
        open(os.path.join(dir_path, "dump", "svm_author_classifier.pkl"), "rb")
    )

    abstract_keywords = ["abstract"]
    introduction_keywords = ["introduction"]
    keywords_keywords = ["keywords", "index terms"]
    affiliation_keywords = [
        "author details",
        "university",
        "department",
        "school",
        "affiliation",
        "institut",
        "institute",
        "laboratory",
        "centre",
        "center",
        "faculty",
        "college",
    ]
    reference_keywords = ["references", "bibliography"]

    def __init__(self):
        """
        Constructor of ScientificExtractor class
        """

        self.pipeline = pipeline(
            "ner", model="topmas/IRyS-NER-Paper", aggregation_strategy="first"
        )

    def preprocess(self, text: str) -> Union[str, List[str]]:
        """
        Preprocess text for scientific domain

        [Arguments]
            text: str -> Text to preprocess
        """
        headers = []
        textsplit = text.splitlines()

        for idx, line in enumerate(textsplit):
            if "Abstract" in line or idx == 20:
                break
            headers.append(line)

        header = "\n".join(headers)
        body = "\n".join(textsplit[len(headers) :])

        preprocessed = nltk.sent_tokenize(body)
        preprocessed = [header] + [sent.replace("\n", " ") for sent in preprocessed]

        return preprocessed

    def extract(self, file: bytes) -> Dict[str, Any]:
        """
        Extract information from a paper file

        [Arguments]
            file: bytes -> File bytes to extract information from
        [Returns]
            Dict -> Dictionary containing extracted information
        """

        result = super().extract(file)

        # TODO: Handle other extension if possible
        if result["extension"] == ".pdf":
            metadata = self.extract_scientific_information(file)
            result = result | metadata
        return result

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text

        [Arguments]
            text: str -> Text to extract entities from
        [Returns]
            List[Dict] -> List of dictionaries containing extracted entities
        """
        preprocessed = self.preprocess(text)
        ner_results = [self.pipeline(sent) for sent in preprocessed]

        full_text = "".join(preprocessed)

        result = []
        cur_len = 0
        for idx, sent in enumerate(preprocessed):
            sent_len = len(sent)
            for ner in ner_results[idx]:
                ner["start"] += cur_len
                ner["end"] += cur_len
                ner["score"] = ner["score"].item()
            cur_len += sent_len
            result += ner_results[idx]

        return NERResult(full_text, result)

    def extract_scientific_information(self, file: bytes) -> Dict[str, Any]:
        """
        Extract scientific metadata from a paper file

        [Arguments]
            file: bytes -> File bytes to extract metadata from
        [Returns]
            Dict -> Dictionary containing extracted metadata
        """

        scientific_information = {
            "title": [],
            "abstract": [],
            "keywords": [],
            "authors": [],
            "affiliations": [],
            "references": [],
        }

        if isinstance(file, bytes):
            doc = fitz.open(stream=file, filetype="pdf")
        else:
            raise TypeError("file must be bytes")

        # Extract pages from document without images
        pages = []
        reference_pages_numbers = []
        for page in doc:
            pages.append(
                page.get_text(
                    "dict",
                    sort=False,
                    flags=(fitz.TEXTFLAGS_DICT | fitz.TEXT_DEHYPHENATE)
                    & ~fitz.TEXT_PRESERVE_IMAGES,
                )
            )
            search = page.search_for("references") + page.search_for("bibliography")
            if search != []:
                reference_pages_numbers.append(page.number)

        # Extract metadata from paper header
        first_page = pages[0]
        document_height = first_page["height"]

        page_lines = []

        abstract_line = 99999
        introduction_line = 99999
        keywords_line = 99999

        max_font_size = 0
        for block in first_page["blocks"]:
            for line in block["lines"]:
                line_text = ""
                span_font_sizes = defaultdict(int)
                span_flags = defaultdict(int)
                for span in line["spans"]:
                    # Ignore span if it is a non space superscript
                    if span["flags"] & 2**0 and not span["text"].isspace():
                        continue
                    span_text = span["text"]
                    line_text += span_text
                    span_font_sizes[span["size"]] += len(span_text)
                    span_flags[span["flags"]] += len(span_text)

                # Ignore empty line
                if not line_text.isspace():
                    # Find most common font size and flag (style)
                    common_font_size = max(span_font_sizes, key=span_font_sizes.get)
                    common_flag = max(span_flags, key=span_flags.get)

                    page_lines.append(
                        {
                            "text": line_text,
                            "label": "unknown",
                            "font_size": common_font_size,
                            "flags": common_flag,
                            "bbox": line["bbox"],
                        }
                    )

                    # Get max font size that are horizontal
                    if common_font_size > max_font_size and line["dir"] == (1.0, 0.0):
                        max_font_size = common_font_size

                    # Find first line that contains abstract
                    if abstract_line == 99999 and any(
                        line_text.lower().startswith(keyword)
                        for keyword in self.abstract_keywords
                    ):
                        abstract_line = len(page_lines) - 1

                    # Find first line that contains introduction
                    if introduction_line == 99999 and any(
                        line_text.lower().startswith(keyword)
                        for keyword in self.introduction_keywords
                    ):
                        introduction_line = len(page_lines) - 1

                    # Find first line that contains keywords
                    if keywords_line == 99999 and any(
                        line_text.lower().startswith(keyword)
                        for keyword in self.keywords_keywords
                    ):
                        keywords_line = len(page_lines) - 1

        # Get breakpoint line for header
        breakpoint_line = min(abstract_line, introduction_line, keywords_line)

        for idx, line in enumerate(page_lines):
            # If located in the header (above breakpoint) or located in the top 1/4 of the page
            if idx < breakpoint_line or line["bbox"][3] < document_height / 4:
                # If the line is the largest font size, add to title
                if line["font_size"] == max_font_size:
                    scientific_information["title"].append(line["text"])
                    line["label"] = "title"
                else:
                    # If the line contains affiliation keywords, add to affiliations
                    if any(
                        keyword in line["text"].lower()
                        for keyword in self.affiliation_keywords
                    ):
                        scientific_information["affiliations"].append(line["text"])
                        line["label"] = "affiliation"
            # If located in the line that contains "Abstract" and after it
            if abstract_line != 99999 and idx >= abstract_line:
                # If line is before the keywords line and introduction line, add to abstract
                if idx < keywords_line and idx < introduction_line:
                    scientific_information["abstract"].append(line["text"])
                    line["label"] = "abstract"

            # If line is in the keywords section
            if keywords_line != 99999 and idx >= keywords_line:
                # If line is before the introduction line, add to keywords
                if introduction_line != 99999 and idx < introduction_line:
                    scientific_information["keywords"].append(line["text"])
                    line["label"] = "keywords"
                # If there is no introduction line, assume keywords takes 2 lines
                # TODO: is there a better heuristic for this? or just assume introduction line is always there?
                elif introduction_line == 99999 and idx < keywords_line + 2:
                    scientific_information["keywords"].append(line["text"])
                    line["label"] = "keywords"

        # Extract authors
        scientific_information["authors"] = self.__classify_authors(
            page_lines, breakpoint_line
        )

        # Extract references
        scientific_information["references"] = self.__extract_references(
            pages, reference_pages_numbers
        )

        # Post process
        return self.__post_process(scientific_information)

    def __classify_authors(
        self, paper_header: List[dict], breakpoint_line: int
    ) -> List[str]:
        """
        Classify authors from paper header

        [Arguments]
            paper_header: List[dict] -> List of lines in paper header
            breakpoint_line: int -> Line number of breakpoint
        [Returns]
            List[str] -> List of author lines
        """

        authors = []
        lines_features = []
        for idx, line in enumerate(paper_header):
            # Calculate line features if before breakpoint and does not only contains whitespace
            if idx < breakpoint_line and not line["text"].isspace():
                if idx == 0 and idx == len(paper_header) - 1:
                    features = self.__calculate_line_features(line)
                if idx == 0:
                    features = self.__calculate_line_features(
                        line, next=paper_header[idx + 1]
                    )
                elif idx == len(paper_header) - 1:
                    features = self.__calculate_line_features(
                        line, prev=paper_header[idx - 1]
                    )
                else:
                    features = self.__calculate_line_features(
                        line, next=paper_header[idx + 1], prev=paper_header[idx - 1]
                    )

                lines_features.append(features)

        dataframe = pd.DataFrame(lines_features)

        # Predict author lines
        author_labels = self.author_classifier.predict(dataframe)

        # Add author lines to authors list
        for idx, label in enumerate(author_labels):
            if label == "Author":
                authors.append(paper_header[idx]["text"])

        return authors

    def __extract_references(
        self, pages: List[dict], reference_pages_numbers: list[int]
    ) -> List[str]:
        """
        Extract references from reference pages

        [Arguments]
            pages: List[dict] -> List of reference pages
        [Returns]
            List[str] -> List of references
        """

        references = []

        if reference_pages_numbers != []:
            reference_pages = pages[reference_pages_numbers[-1] :]
            first_reference_page = reference_pages[0]
            reference_lines = []
            block_texts = []

            reference_header_line = 99999
            references_header_block = len(first_reference_page["blocks"]) + 1
            reference_header_found = False

            # Find reference header line
            for id, page in enumerate(reference_pages):
                for idx, block in enumerate(page["blocks"]):
                    block_text = ""
                    block_font_sizes = defaultdict(int)
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            line_text += span["text"]
                            block_font_sizes[span["size"]] += len(span["text"])
                        reference_lines.append(line_text)
                        block_text += line_text

                        # Find if reference in line_text
                        if id == 0 and not reference_header_found:
                            if any(
                                keyword in line_text.lower()
                                for keyword in self.reference_keywords
                            ):
                                references_header_block = idx
                                reference_header_line = len(reference_lines)
                                break

                    common_font_size = max(block_font_sizes, key=block_font_sizes.get)
                    block_texts.append(
                        {"text": block_text, "font_size": common_font_size}
                    )

            reference_block_texts = []

            # If the header is not the last block, the blocks after is assumed to be the references
            if references_header_block != len(first_reference_page["blocks"]) - 1:
                current_block = references_header_block + 1
                reference_font_size = first_reference_page["blocks"][current_block][
                    "lines"
                ][0]["spans"][0]["size"]
                reference_block_texts = block_texts[current_block:]

                # Get the font size of the references, skip empty blocks
                while (
                    current_block < len(first_reference_page["blocks"])
                    and block_texts[current_block]["text"].isspace()
                ):
                    current_block += 1
                    reference_font_size = block_texts[current_block]["font_size"]
                    reference_block_texts = block_texts[current_block:]

                # Add reference until line with different font size and contains letters
                for block in reference_block_texts:
                    if (
                        block["font_size"] == reference_font_size
                        or block["text"].isspace()
                        or block["text"].isnumeric()
                    ):
                        if not (block["text"].isnumeric() or block["text"].isspace()):
                            references.append(block["text"])
                    else:
                        break
            # Try to extract reference using lines (in case of wrong extraction)
            # TODO: check if this is correct
            else:
                references = ""
                if reference_header_line != 99999:
                    reference_lines = reference_lines[reference_header_line:]
                    for line in reference_lines:
                        if line.isspace() or line.isnumeric():
                            continue
                        else:
                            references += line

        return references

    def __calculate_line_features(
        self, line: dict, prev: dict = None, next: dict = None
    ) -> dict:
        """
        Calculate features for a line to be used for classification

        [Arguments]
            line: dict -> Line to calculate features for
            prev: dict -> Previous line
            next: dict -> Next line
        [Returns]
            dict -> Dictionary of features
        """

        text = line["text"]
        flags = line["flags"]
        font_size = line["font_size"]

        caps_count = 0
        at_count = 0
        num_count = 0
        affiliation_count = 0
        comma_count = 0
        punct_count = 0

        for char in text:
            if char.isupper():
                caps_count += 1
            if char == "@":
                at_count += 1
            if char.isdigit():
                num_count += 1
            if char in string.punctuation:
                punct_count += 1
            if char == ",":
                comma_count += 1

        for word in self.affiliation_keywords:
            if word in text.lower():
                affiliation_count += 1

        return {
            "label": line["label"],
            "caps_count": caps_count,
            "at_count": at_count,
            "num_count": num_count,
            "affiliation_count": affiliation_count,
            "comma_count": comma_count,
            "comma_percent": comma_count / len(text) if len(text) > 0 else 0,
            "punct_count": punct_count,
            "punct_percent": punct_count / len(text) if len(text) > 0 else 0,
            "prev_label": prev["label"] if prev else "unknown",
            "next_label": next["label"] if next else "unknown",
            "same_characteristic_prev": int(
                prev["flags"] == flags and prev["font_size"] == font_size
            )
            if prev
            else 0,
            "same_characteristic_next": int(
                next["flags"] == flags and next["font_size"] == font_size
            )
            if next
            else 0,
        }

    def __post_process(self, metadata: dict) -> dict:
        """
        Post process metadata

        [Arguments]
            metadata: dict -> Metadata to post process
        [Returns]
            dict -> Post processed metadata
        """

        # Process title
        metadata["title"] = " ".join([text.strip() for text in metadata["title"]])

        # Process authors
        author_pattern = re.compile(r",\s+(?:and)?|\s+and")
        author_split = author_pattern.split
        authors = [
            part.strip()
            for author in metadata["authors"]
            for part in author_split(author)
            if part
        ]
        metadata["authors"] = authors

        # Process affiliations
        # TODO: Should there be preprocessing for affiliation
        #       e.g. when one affiliation is split in two or more lines
        affiliations = [text.strip() for text in metadata["affiliations"]]
        metadata["affiliations"] = affiliations

        # Process abstract
        if metadata["abstract"] != []:
            abstract_text = " ".join([text.strip() for text in metadata["abstract"]])
            if abstract_text.lower().startswith("abstract"):
                abstract_text = abstract_text[8:]
            metadata["abstract"] = re.sub(r"^\W+", "", abstract_text)

        # Process keywords
        if metadata["keywords"] != []:
            keywords_text = " ".join([text.strip() for text in metadata["keywords"]])
            for word in self.keywords_keywords:
                if word in keywords_text.lower():
                    keywords_text = keywords_text[len(word) :]
                    break
            keywords_text = re.sub(r"^\W+", "", keywords_text)
            metadata["keywords"] = re.split(r"\s*[,;|]\s*", keywords_text)

        # Process references
        # TODO: Is there a better way to do this? as this assumes the references are in the format '[1] ...'
        number_pattern = re.compile(
            r"\[\d+\]"
        )  # pattern to match '[...]' with digits inside
        number_split = number_pattern.split  # function to split text using the pattern
        references = [
            part.strip()
            for reference in metadata["references"]
            for part in number_split(reference)
            if part and not number_pattern.match(part)
        ]
        metadata["references"] = references

        return metadata
