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


class EmailAlreadyVerifiedException(CustomException):
    code = 403
    error_code = "USER__EMAIL_ALREADY_VERIFIED"
    message = "Email is already verified"


class EmailNotVerifiedException(CustomException):
    code = 403
    error_code = "USER__EMAIL_NOT_VERIFIED"
    message = "Email is not verified"


class ForgotPasswordOTPNotVerifiedException(CustomException):
    code = 403
    error_code = "USER__FORGOT_PASSWORD_OTP_NOT_VERIFIED"
    message = "Forgot password OTP is not verified"


class ForgotPasswordOTPVerifiedException(CustomException):
    code = 403
    error_code = "USER__FORGOT_PASSWORD_OTP_ALREADY_VERIFIED"
    message = "Forgot password OTP has already been verified"


class ForgotPasswordOTPExpiredException(CustomException):
    code = 403
    error_code = "USER__FORGOT_PASSWORD_OTP_EXPIRED"
    message = "Forgot password OTP is expired"


class WrongForgotPasswordOTPException(CustomException):
    code = 403
    error_code = "USER__WRONG_FORGOT_PASSWORD_OTP"
    message = "Wrong forgot password OTP"


class ForgotPasswordOTPAlreadySentException(CustomException):
    code = 429
    error_code = "USER__FORGOT_PASSWORD_OTP_ALREADY_SENT"
    message = "Forgot password OTP has already been sent"


class NotAllowedException(CustomException):
    code = 403
    error_code = "USER__NOT_ALLOWED"
    message = "You are not allowed to perform this action"
