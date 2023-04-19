from core.exceptions import CustomException


class RepositoryDetailsEmptyException(CustomException):
    code = 400
    error_code = "REPOSITORY__DETAILS_EMPTY"
    message = "name, description, or repository publicity cannot be empty"


class RepositoryNotFoundException(CustomException):
    code = 404
    error_code = "REPOSITORY__NOT_FOUND"
    message = "Repository not found"


class InvalidRepositoryRoleException(CustomException):
    code = 400
    error_code = "REPOSITORY__INVALID_ROLE"
    message = "Invalid repository role"


class DuplicateCollaboratorException(CustomException):
    code = 422
    error_code = "REPOSITORY__DUPLICATE_COLLABORATOR"
    message = "User is already a collaborator of this repository"


class InvalidRepositoryCollaboratorException(CustomException):
    code = 400
    error_code = "REPOSITORY__INVALID_COLLABORATOR"
    message = "Invalid collaborator"
