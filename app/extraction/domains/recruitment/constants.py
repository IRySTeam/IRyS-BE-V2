import os
import re
from collections import defaultdict

dir_path = os.path.dirname(os.path.realpath(__file__))

RESUME_SECTIONS_KEYWORDS = {
    "profile": [
        "profile",
        "objective",
        "career objective",
        "career summary",
        "summary",
        "personal profile",
        "objective",
    ],
    "experience": [
        "experience",
        "professional experience",
        "work experience",
        "work history",
        "working experience",
        "working history",
        "career history",
        "employment history",
        "employment",
        "professional backgrouund",
        "professional summary",
        "professional experience",
        "selected experience",
    ],
    "projects": [
        "projects",
        "personal projects",
        "project experience",
        "project summary",
        "project details",
        "project description",
        "project highlights",
        "project overview",
        "project responsibilities",
        "project summary",
        "project title",
        "project work",
    ],
    "education": [
        "education",
        "education and training",
        "academic background",
        "academic qualifications",
        "course",
        "courses",
        "course details",
        "related courses",
        "related course",
        "studies",
        "workshops",
        "workshop",
    ],
    "certifications": [
        "certifications",
        "certification",
        "certification details",
        "licences",
    ],
    "skills": [
        "skills",
        "skill",
        "skill set",
        "abilities",
        "ability",
        "technical skills",
        "technical skill",
        "areas of expertise",
        "areas of knowledge",
        "qualifications",
        "qualification",
        "strengths",
        "strength",
        "expertise",
    ],
    "misc": [
        "hobbies",
        "interests",
        "personal interests",
        "strengths",
        "strength",
        "leadership",
        "awards",
        "award",
        "honors",
        "extracurricular activities",
        "publications",
        "links",
        "assessments",
    ],
}

# Create inverted dictionary to map keywords to category
RESUME_SECTIONS_KEYWORDS_INV = defaultdict(str)
for key, value in RESUME_SECTIONS_KEYWORDS.items():
    for v in value:
        RESUME_SECTIONS_KEYWORDS_INV[v] = key

RESUME_HEADERS = RESUME_SECTIONS_KEYWORDS_INV.keys()

RESUME_HEADERS_REGEX = re.compile(
    r"(" + r")|(".join(re.escape(s) for s in RESUME_HEADERS) + r")", re.IGNORECASE
)

INSTITUTION_KEYWORDS = [
    "university",
    "universitas",
    "department",
    "school",
    "institut",
    "institute",
    "laboratory",
    "centre",
    "center",
    "faculty",
    "college",
]

INSTITUTION_REGEX = re.compile(
    r"\b(" + r"|".join(re.escape(s) for s in INSTITUTION_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# Skills regex from skills.txt
# Skills list from https://lightcast.io/open-skills
with open(os.path.join(dir_path, "skills.txt"), "r") as f:
    SKILLS = f.read().splitlines()

pattern = re.compile(r"(.+)\s+\(.+\)$")
no_brackets = [m.group(1) for m in (pattern.match(line) for line in SKILLS) if m]
SKILLS += no_brackets

SKILLS_REGEX = re.compile(
    r"\b(" + r"|".join(re.escape(s) for s in SKILLS) + r")\b", re.IGNORECASE
)

# Job titles regex from job_titles.txt
# Job titles list from https://lightcast.io/open-skills
with open(os.path.join(dir_path, "job_titles.txt"), "r") as f:
    JOB_TITLES = f.read().splitlines()

JOB_TITLES_REGEX = re.compile(
    r"(\b(?:junior|senior)\b)?"
    + r"\b("
    + r"|".join(re.escape(s) for s in JOB_TITLES)
    + r")\b",
    re.IGNORECASE,
)

# Date regex
MONTH_REGEX = re.compile(
    r"(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|"
    r"jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|"
    r"dec(ember)?)",
    re.IGNORECASE,
)
YEAR_REGEX = re.compile(r"((19|20)\d\d)")
WORD_DATE_REGEX = re.compile(
    MONTH_REGEX.pattern + r"?" + r"\s*" + YEAR_REGEX.pattern, re.IGNORECASE
)

NUMBER_DATE_REGEX = re.compile(
    r"\b((0?[1-9]|[1-2]\d|3[01])\/(19|20)?\d\d)\b", re.IGNORECASE
)

DATE_RANGE_REGEX = re.compile(
    r"(?P<start_date>(?:"
    + WORD_DATE_REGEX.pattern
    + r"|"
    + NUMBER_DATE_REGEX.pattern
    + r"))"
    + r"\s*(?:-|to|\s+)\s*"
    + r"(?P<end_date>(?:"
    + WORD_DATE_REGEX.pattern
    + r"|"
    + NUMBER_DATE_REGEX.pattern
    + r"|(?:current|present|now)))",
    re.IGNORECASE,
)

# Email regex
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+", re.IGNORECASE)
