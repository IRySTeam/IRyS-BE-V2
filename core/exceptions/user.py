from core.exceptions import CustomException


class PasswordDoesNotMatchException(CustomException):
    code = 401
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "password does not match"


class DuplicateEmailException(CustomException):
    code = 400
    error_code = "USER__DUPLICATE_EMAIL"
    message = "A user with same email already exists"


class UserNotFoundException(CustomException):
    code = 404
    error_code = "USER__NOT_FOUND"
    message = "user not found"


class ExpiredOTPException(CustomException):
    code = 400
    error_code = "USER__EXPIRED_OTP"
    message = "OTP is expired"


class WrongOTPException(CustomException):
    code = 400
    error_code = "USER__WRONG_OTP"
    message = "Wrong OTP"


class InvalidEmailException(CustomException):
    code = 400
    error_code = "USER__INVALID_EMAIL"
    message = "Email is not valid"


class InvalidPasswordException(CustomException):
    code = 400
    error_code = "USER__INVALID_PASSWORD"
    message = "Password is not valid"