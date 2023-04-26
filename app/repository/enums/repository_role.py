from enum import Enum


class RepositoryRole(Enum):
    """Enum for repository roles."""

    OWNER = 4
    ADMIN = 3
    UPLOADER = 2
    VIEWER = 1

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
