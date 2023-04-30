from enum import Enum


class IndexingStatusEnum(Enum):
    READY = "READY"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    INDEXING = "INDEXING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class DocumentRole(Enum):
    """Enum for document roles."""

    OWNER = 3
    EDITOR = 2
    VIEWER = 1

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
