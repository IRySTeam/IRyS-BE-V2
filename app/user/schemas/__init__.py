from .request import *
from .response import *


class ExceptionResponseSchema(BaseModel):
    error: str
