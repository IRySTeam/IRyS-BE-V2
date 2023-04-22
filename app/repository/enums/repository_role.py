from enum import Enum


class RepositoryRole(Enum):
    """Enum for repository roles."""

    OWNER = 4
    ADMIN = 3
    UPLOADER = 2
    VIEWER = 1
