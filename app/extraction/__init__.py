from app.extraction.domain import NER, PaperNER, RecruitmentNER
from app.extraction.nerresult import NERResult

NERModel = NER()
PaperNERModel = PaperNER()
RecruitmentNERModel = RecruitmentNER()

__all__ = [
    "NERModel",
    "PaperNERModel",
    "RecruitmentNERModel",
    "NERResult",
]
