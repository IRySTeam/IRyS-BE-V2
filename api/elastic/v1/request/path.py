from dataclasses import dataclass
from fastapi import Path

@dataclass
class GetIndexPathParams:
    index_name: str = Path(..., description="Name of the new index")

@dataclass
class UpdateIndexPathParams:
    index_name: str = Path(..., description="Name of the index to be updated")

@dataclass
class DeleteIndexPathParams:
    index_name: str = Path(..., description="Name of the index to be deleted")

@dataclass
class IndexDocumentPathParams:
    index_name: str = Path(..., description="Name of the index to add the document to")