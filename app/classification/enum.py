from enum import Enum


class LabelEnum(Enum):
    OTHER = "__other__"
    RESUME = "__resume__"
    PAPER = "__paper__"


map_string_to_enum_label = {
    "General": "__other__",
    "Scientific": "__paper__",
    "Recruitment": "__resume__",
}
