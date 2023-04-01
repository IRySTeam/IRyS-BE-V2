from dataclasses import dataclass
from fastapi import Query

@dataclass
class GetAllIndexQueryParams:
    all: bool = Query(False, description="Whether to return auto-generated indices or not")