import re
from collections import defaultdict
from typing import Any, Dict, List

import fitz
from transformers import pipeline

from app.extraction.domains.recruitment.constants import (
    DATE_RANGE_REGEX,
    EMAIL_REGEX,
    INSTITUTION_REGEX,
    JOB_TITLES_REGEX,
    RESUME_HEADERS_REGEX,
    RESUME_SECTIONS_KEYWORDS_INV,
    SKILLS_REGEX,
)
from app.extraction.general_extractor import GeneralExtractor


class RecruitmentExtractor(GeneralExtractor):
    """
    Recruitment extractor class
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
        # TODO: Handle other extension if possible
        if result["extension"] == ".pdf":
            recruitment_information = self.extract_recruitment_information(file)
            result = result | recruitment_information

        return result

    def extract_recruitment_information(self, file: bytes) -> Dict[str, Any]:
        recruitment_information = {
            "name": "",
            "email": "",
            "experiences": [],
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
        }

        if isinstance(file, bytes):
            doc = fitz.open(stream=file, filetype="pdf")
        else:
            raise TypeError("file must be bytes")

        pages = []
        dict_flags = (
            (fitz.TEXTFLAGS_DICT | fitz.TEXT_DEHYPHENATE)
            & ~fitz.TEXT_PRESERVE_IMAGES
            & ~fitz.TEXT_PRESERVE_LIGATURES
        )
        text_flags = (
            (fitz.TEXTFLAGS_TEXT | fitz.TEXT_DEHYPHENATE)
            & ~fitz.TEXT_PRESERVE_IMAGES
            & ~fitz.TEXT_PRESERVE_LIGATURES
        )
        resume_text = ""
        for page in doc:
            pages.append(page.get_text("dict", sort=False, flags=dict_flags))
            resume_text += page.get_text("text", sort=False, flags=text_flags)

        page_lines = []
        max_font_size = 0
        header_font_size = 0
        possible_header_sizes = [0]
        for page in pages:
            for block in page["blocks"]:
                for line in block["lines"]:
                    line_text = ""
                    span_font_sizes = defaultdict(int)
                    span_flags = defaultdict(int)
                    for span in line["spans"]:

                        line_text += span["text"]
                        span_font_sizes[span["size"]] += len(span["text"])
                        span_flags[span["flags"]] += len(span["text"])

                    if not line_text == "" and not line_text.isspace():
                        common_font_size = max(span_font_sizes, key=span_font_sizes.get)
                        if re.match(RESUME_HEADERS_REGEX, line_text):
                            possible_header_sizes.append(common_font_size)
                        common_flag = max(span_flags, key=span_flags.get)
                        page_lines.append(
                            {
                                "text": line_text.encode("ascii", errors="ignore")
                                .decode()
                                .strip(),
                                "block": block["number"],
                                "label": "unknown",
                                "size": common_font_size,
                                "flags": common_flag,
                                "bbox": line["bbox"],
                            }
                        )

                        # Get max font size that are horizontal
                        if common_font_size > max_font_size and line["dir"] == (
                            1.0,
                            0.0,
                        ):
                            max_font_size = common_font_size

        header_font_size = max(possible_header_sizes)

        i = 0
        resume_segment = []
        current_text = ""
        current_label = "profile"
        resume_segments = defaultdict(list)
        while i < len(page_lines):
            # Match line text with resume header regex and font size
            match = re.match(RESUME_HEADERS_REGEX, page_lines[i]["text"].lower())
            while not (match and page_lines[i]["size"] == header_font_size):
                resume_segment.append(page_lines[i])
                current_text += page_lines[i]["text"] + "\n"
                page_lines[i]["label"] = current_label
                i += 1
                if i == len(page_lines):
                    break
                match = re.match(RESUME_HEADERS_REGEX, page_lines[i]["text"].lower())

            resume_segments[current_label] += resume_segment

            if i < len(page_lines):
                if match:
                    current_label = RESUME_SECTIONS_KEYWORDS_INV[match.group()]
                    page_lines[i]["label"] = current_label
                else:
                    current_label = "unknown"
                resume_segment = []
                current_text = ""
                resume_segment.append(page_lines[i])

            i += 1

        # Extract name and email from profile segment
        name = self.__extract_name(resume_segments["profile"])
        recruitment_information["name"] = name

        # Extract email
        email = self.__extract_email(resume_text)
        recruitment_information["email"] = email

        # Extract skills from skills segment
        skills = self.__extract_skills(resume_segments["skills"])
        recruitment_information["skills"] = skills

        # Extract experiences
        recruitment_information |= self.__extract_experiences(
            resume_segments["experience"]
        )

        # Extract education
        recruitment_information |= self.__extract_educations(
            resume_segments["education"]
        )

        # Extract projects
        recruitment_information |= self.__extract_projects(resume_segments["projects"])

        # Extract certifications
        recruitment_information |= self.__extract_certifications(
            resume_segments["certifications"]
        )

        return recruitment_information

    def __extract_name(self, profile_segment: List[Dict[str, Any]]) -> str:
        """
        Extract name and email from profile segment

        [Arguments]
            profile_segment: List -> Profile segment
        [Returns]
            Tuple[str, str] -> Tuple of name and email
        """

        name = ""

        # Assume the name is the text with the largest font size in the profile segment
        profile_max_font_size = 0
        for line in profile_segment:
            if line["size"] > profile_max_font_size:
                profile_max_font_size = line["size"]
                name = line["text"]
        return name

    def __extract_email(self, text: str) -> str:
        """
        Extract email from text

        [Arguments]
            text: str -> Text
        [Returns]
            str -> Email
        """

        match = re.search(EMAIL_REGEX, text)
        if match:
            return match.group()
        return ""

    def __extract_skills(self, skills_segment: List[Dict[str, Any]]) -> List[str]:
        """
        Extract skills from skills segment

        [Arguments]
            skills_segment: List -> Skills segment
        [Returns]
            List[str] -> List of skills
        """

        skills = []
        for line in skills_segment:
            # Handle multiple skills in one line separated by comma
            skill_list = line["text"].strip().split(",")
            for skill in skill_list:
                match = re.match(SKILLS_REGEX, skill.strip())
                if match:
                    skills.append(match.string)

        return skills

    def __extract_experiences(
        self, experiences_segment: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract experiences from experiences segment

        [Arguments]
            experiences_segment: List -> Experiences segment
        [Returns]
            List[Dict[str, Any]] -> List of experiences
        """

        # TODO: Add job titles from NER if needed
        # job_from_ent = []
        # for jobent in role_ent:
        #     # check the span to avoid duplicates
        #     # print(f"{jobent=}")
        #     if not any(span_overlap(job["span"], (jobent["start"], jobent["end"])) for job in jobtitles):
        #         job_from_ent.append({
        #             "string": jobent["word"],
        #             "span": (jobent["start"], jobent["end"])
        #         })

        job_titles = []
        dates = []
        dates_idxs = []
        first_date_idx = -1
        first_job_title_idx = -1
        current_length = 0
        first_type = ""

        # Try to get first type after the header (dates, job title, or company)
        for idx, line in enumerate(experiences_segment):
            type = "unknown"

            # Get regex match for job title
            match = re.match(JOB_TITLES_REGEX, line["text"].strip())
            if match:
                if first_job_title_idx == -1:
                    first_job_title_idx = idx
                span = match.span()
                job_titles.append(
                    {
                        "string": match.string,
                        "span": (current_length + span[0], current_length + span[1]),
                    }
                )
                type = "job_title"

            # Get experience date range
            match = re.match(DATE_RANGE_REGEX, line["text"].strip())
            if match:
                if first_date_idx == -1:
                    first_date_idx = idx
                dates.append((match.group("start_date"), match.group("end_date")))
                dates_idxs.append(idx)
                type = "date"

            if idx == 1 and first_type == "":
                first_type = type

            current_length += len(line["text"]) + 1

        # job_titles += job_from_ent
        # job_titles = sorted(job_titles, key=lambda x: x["span"][0])

        # Try to get the order of job title, date, and company in the resume
        experiences = []
        job_titles_out = []
        companies_out = []
        descriptions_out = []
        if len(dates_idxs) > 0:
            if first_job_title_idx != -1:
                closest_date = min(
                    dates_idxs, key=lambda x: abs(x - first_job_title_idx)
                )
                date_to_job_title = first_job_title_idx - closest_date
                job_title_idxs = [idx + date_to_job_title for idx in dates_idxs]

                # Assume if type is unknown, then it is company
                if first_type == "unknown":
                    first_type = "company"

                    date_to_company = 1 - dates_idxs[0]
                elif first_type == "date":
                    is_job_title_second = job_title_idxs[0] == 2
                    if is_job_title_second:
                        date_to_company = 3 - dates_idxs[0]
                    else:  # Company is second
                        date_to_company = 2 - dates_idxs[0]
                else:  # First type is job title
                    is_date_second = dates_idxs[0] == 2
                    if is_date_second:
                        date_to_company = 3 - dates_idxs[0]
                    else:
                        date_to_company = 2 - dates_idxs[0]

                company_idxs = [idx + date_to_company for idx in dates_idxs]

                start_offset = first_date_idx - 1
                exp_start_idxs = [idx - start_offset for idx in dates_idxs]

                for idx, start_idx in enumerate(exp_start_idxs):
                    end_idx = (
                        exp_start_idxs[idx + 1]
                        if idx < len(exp_start_idxs) - 1
                        else len(experiences_segment)
                    )
                    current_experience = experiences_segment[start_idx:end_idx]
                    non_desc_idxs = [
                        job_title_idxs[idx] - start_idx,
                        company_idxs[idx] - start_idx,
                        dates_idxs[idx] - start_idx,
                    ]
                    description = "\n".join(
                        [
                            line["text"]
                            for idx, line in enumerate(current_experience)
                            if idx not in non_desc_idxs
                        ]
                    )

                    job_title = experiences_segment[job_title_idxs[idx]]["text"]
                    company = experiences_segment[company_idxs[idx]]["text"]

                    experiences.append(
                        {
                            "job_title": job_title,
                            "company": company,
                            "start_date": dates[idx][0],
                            "end_date": dates[idx][1],
                            "description": description,
                        }
                    )

                    job_titles_out.append(job_title)
                    companies_out.append(company)
                    descriptions_out.append(description)

        output = {
            "experiences": experiences,
            "experiences_job_titles": job_titles_out,
            "experiences_companies": companies_out,
            "experiences_descriptions": descriptions_out,
        }

        return output

    def __extract_educations(
        self, educations_segment: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract educations from educations segment

        [Arguments]
            educations_segment: List -> Educations segment
        [Returns]
            List[Dict[str, Any]] -> List of educations
        """

        institutions = []
        dates = []
        dates_idxs = []
        first_institution_idx = -1
        first_date_idx = -1
        current_length = 0
        first_type = ""
        for idx, line in enumerate(educations_segment):
            type = "unknown"

            # Get regex match for institution/school name
            match = re.search(INSTITUTION_REGEX, line["text"].strip())
            if match:
                if first_institution_idx == -1:
                    first_institution_idx = idx
                span = match.span()
                institutions.append(
                    {
                        "string": match.string,
                        "span": (current_length + span[0], current_length + span[1]),
                    }
                )
                type = "institution"

            # Get education date range
            match = re.match(DATE_RANGE_REGEX, line["text"].strip())
            if match:
                if first_date_idx == -1:
                    first_date_idx = idx
                dates.append((match.group("start_date"), match.group("end_date")))
                dates_idxs.append(idx)
                type = "date"

            if idx == 1 and first_type == "":
                first_type = type

            current_length += len(line["text"]) + 1

        educations = []
        institutions_out = []
        degrees_out = []
        descriptions_out = []

        if len(dates_idxs) > 0:
            if first_institution_idx != -1:
                closest_date = min(
                    dates_idxs, key=lambda x: abs(x - first_institution_idx)
                )
                date_to_institution = first_institution_idx - closest_date
                institutions_idxs = [idx + date_to_institution for idx in dates_idxs]

                if first_type == "unknown":
                    first_type = "degree"

                    degree_to_date = 1 - dates_idxs[0]
                elif first_type == "date":
                    second_jobtitle = institutions_idxs[0] == 2
                    if second_jobtitle:
                        degree_to_date = 3 - dates_idxs[0]
                    else:
                        degree_to_date = 2 - dates_idxs[0]
                else:
                    second_date = dates_idxs[0] == 2
                    if second_date:
                        degree_to_date = 3 - dates_idxs[0]
                    else:
                        degree_to_date = 2 - dates_idxs[0]

                degree_idxs = [idx + degree_to_date for idx in dates_idxs]
                start_red = first_date_idx - 1
                edu_start_idxs = [idx - start_red for idx in dates_idxs]

                for idx, start_idx in enumerate(edu_start_idxs):
                    end_idx = (
                        edu_start_idxs[idx + 1]
                        if idx < len(edu_start_idxs) - 1
                        else len(educations_segment)
                    )
                    current_education = educations_segment[start_idx:end_idx]
                    non_desc_edu_idxs = [
                        institutions_idxs[idx] - start_idx,
                        degree_idxs[idx] - start_idx,
                        dates_idxs[idx] - start_idx,
                    ]
                    description = "\n".join(
                        [
                            line["text"]
                            for idx, line in enumerate(current_education)
                            if idx not in non_desc_edu_idxs
                        ]
                    )

                    institution = educations_segment[institutions_idxs[idx]]["text"]
                    degree = educations_segment[degree_idxs[idx]]["text"]

                    educations.append(
                        {
                            "institution": institution,
                            "degree": degree,
                            "start_date": dates[idx][0],
                            "end_date": dates[idx][1],
                            "description": description,
                        }
                    )

                    institutions_out.append(institution)
                    degrees_out.append(degree)
                    descriptions_out.append(description)

        output = {
            "education": educations,
            "education_institutions": institutions_out,
            "education_degrees": degrees_out,
            "education_descriptions": descriptions_out,
        }

        return output

    def __extract_projects(
        self, projects_segment: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract projects from projects segment

        [Arguments]
            projects_segment: List -> Projects segment
        [Returns]
            List[Dict[str, Any]] -> List of projects
        """

        projects = []
        titles_out = []
        descriptions_out = []

        if len(projects_segment) > 0:
            # Assume the first line of a project entry is the title
            project_title_font_size = projects_segment[1]["size"]
            project_title_flags = projects_segment[1]["flags"]

            current_project = {}
            current_project_title = ""
            current_project_description = ""

            for line in projects_segment[1:]:
                # Check if line is a project title
                if (
                    line["size"] == project_title_font_size
                    and line["flags"] == project_title_flags
                ):
                    if current_project_title != "":
                        current_project["title"] = current_project_title
                        current_project["description"] = current_project_description
                        projects.append(current_project)
                        titles_out.append(current_project_title)
                        descriptions_out.append(current_project_description)
                        current_project = {}
                        current_project_title = ""
                        current_project_description = ""
                    current_project_title = line["text"]
                else:
                    current_project_description += line["text"] + "\n"

            if current_project_title != "":
                current_project["title"] = current_project_title
                current_project["description"] = current_project_description
                projects.append(current_project)
                titles_out.append(current_project_title)
                descriptions_out.append(current_project_description)

        output = {
            "projects": projects,
            "projects_titles": titles_out,
            "projects_descriptions": descriptions_out,
        }

        return output

    def __extract_certifications(
        self, certifications_segment: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract certifications from certifications segment

        [Arguments]
            certifications_segment: List -> Certifications segment
        [Returns]
            List[Dict[str, Any]] -> List of certifications
        """

        certifications = []
        titles_out = []
        descriptions_out = []

        if len(certifications_segment) > 0:
            # Assume the first line of a project entry is the title
            project_title_font_size = certifications_segment[1]["size"]
            project_title_flags = certifications_segment[1]["flags"]

            current_certifications = {}
            current_certification_title = ""
            current_certification_description = ""

            for line in certifications_segment[1:]:
                # Check if line is a project title
                if (
                    line["size"] == project_title_font_size
                    and line["flags"] == project_title_flags
                ):
                    if current_certification_title != "":
                        current_certifications["title"] = current_certification_title
                        current_certifications[
                            "description"
                        ] = current_certification_description
                        certifications.append(current_certifications)
                        titles_out.append(current_certification_title)
                        descriptions_out.append(current_certification_description)
                        current_certifications = {}
                        current_certification_title = ""
                        current_certification_description = ""
                    current_certification_title = line["text"]
                else:
                    current_certification_description += line["text"] + "\n"

            if current_certification_title != "":
                current_certifications["title"] = current_certification_title
                current_certifications[
                    "description"
                ] = current_certification_description
                certifications.append(current_certifications)
                titles_out.append(current_certification_title)
                descriptions_out.append(current_certification_description)

        output = {
            "certifications": certifications,
            "certifications_titles": titles_out,
            "certifications_descriptions": descriptions_out,
        }

        return output

    # def __span_overlap(self, span1: Tuple[int, int], span2: Tuple[int, int]) -> bool:
    #     """
    #     Check if two spans overlap

    #     [Arguments]
    #         span1: tuple[int] -> First span
    #         span2: tuple[int] -> Second span
    #     [Returns]
    #         bool -> True if spans overlap, False otherwise
    #     """

    #     return span1[0] <= span2[0] <= span1[1] or span2[0] <= span1[0] <= span2[1]
