# Import CustomException
from core.exceptions import CustomException


class CustomExceptionHelper:
    @staticmethod
    def get_exception_response(exception: CustomException, description: str) -> dict:
        return {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "code": exception.code,
                        "error_code": exception.error_code,
                        "message": exception.message,
                    }
                }
            },
        }
