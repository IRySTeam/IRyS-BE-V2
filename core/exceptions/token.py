from core.exceptions import CustomException


class DecodeTokenException(CustomException):
    code = 400
    error_code = "TOKEN__DECODE_ERROR"
    message = "token decode error"


class InvalidTokenException(CustomException):
    code = 400
    error_code = "TOKEN__INVALID_TOKEN"
    message = "invalid token"


class ExpiredTokenException(CustomException):
    code = 400
    error_code = "TOKEN__EXPIRE_TOKEN"
    message = "expired token"

class TokenAlreadyUsedException(CustomException):
    code = 409
    error_code = "TOKEN__TOKEN_ALREADY_USED"
    message = "token already used, please request a new one"
