from dataclasses import dataclass
from fastapi import Path

@dataclass
class DomainEntitiesPathParams:
    domain: str = Path(..., description="Domain name")
