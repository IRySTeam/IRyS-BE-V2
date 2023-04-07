from . import BaseEnum


class IndexingStatusEnum(BaseEnum):
    READY = "READY"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    INDEXING = "INDEXING"
    FAILED = "FAILED"
