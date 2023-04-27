from core.exceptions import CustomException


class DocumentNotFoundException(CustomException):
    code = 404
    error_code = "DOCUMENT__NOT_FOUND"
    message = "Document not found"


class InvalidDocumentRoleException(CustomException):
    code = 400
    error_code = "DOCUMENT__INVALID_ROLE"
    message = "Invalid document role"
