from typing import Optional

from pydantic import BaseModel


class EditDocumentRequestSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    content: Optional[str]
    is_public: Optional[bool]
