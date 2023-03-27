from dataclasses import dataclass
from fastapi import Path

@dataclass
class IndexNamePathParams:
    index_name: str = Path(..., description="Name of the index")
