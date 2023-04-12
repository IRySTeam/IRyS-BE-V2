from typing import Optional
from elasticsearch.exceptions import ApiError

from core.exceptions import (
    CustomException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    FailedDependencyException,
)


def classify_error(error: ApiError) -> CustomException:
    """
    Classify the error from Elasticsearch to the corresponding exception.
    [Parameters]
      error: ApiError -> Error from Elasticsearch.
    [Returns]
      CustomException: Exception that is classified from the error.
    """
    reason = find_reason(error)
    print(reason)
    if error.status_code == 400:
        return BadRequestException(reason)
    elif error.status_code == 401:
        return UnauthorizedException(reason)
    elif error.status_code == 403:
        return ForbiddenException(reason)
    elif error.status_code == 404:
        return NotFoundException(reason)
    elif error.status_code == 409:
        return ConflictException(reason)
    else:
        reason = reason or "Failed to connect to Elasticsearch."
        return FailedDependencyException(reason)


def find_reason(err: ApiError) -> Optional[str]:
    """
    Find the reason from the error.
    [Parameters]
      error: ApiError -> Error from Elasticsearch.
    [Returns]
      Optional[str]: Reason from the error.
    """
    reason = None
    try:
        if err.body and isinstance(err.body, dict) and "error" in err.body:
            if isinstance(err.body["error"], dict):
                root_cause = err.body["error"]["root_cause"][0]
                reason = root_cause["reason"] or err.body["error"]["reason"]
            else:
                reason = err.body["error"]
    except LookupError:
        pass
    return reason
