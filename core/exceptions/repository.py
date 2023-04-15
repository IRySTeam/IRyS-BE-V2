from core.exceptions import CustomException


class RepositoryDetailsEmptyException(CustomException):
    code = 400
    error_code = "REPOSITORY__DETAILS_EMPTY"
    message = "name, description, or repository publicity cannot be empty"
