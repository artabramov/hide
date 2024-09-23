"""
This module provides a custom HTTP exception class E, for detailed
error reporting in the applications. The E class extends HTTPException
to include additional error details such as location, input, type,
and HTTP status code. It defines various error codes for common issues,
including token-related errors, user status problems, resource access
issues, and value validation errors. By using this exception class,
we can deliver more granular and actionable error information in API
responses, aiding both debugging and user experience.
"""

from fastapi import HTTPException

SERVER_ERROR = "Internal server error"


class E(HTTPException):
    """
    Custom HTTP exception class for detailed error reporting, allowing
    specification of error location, input, type and HTTP status code.
    This class helps to provide more granular error information in
    responses, useful for debugging and user experience.
    """
    # possible error locations
    LOC_HEADER = "header"
    LOC_COOKIE = "cookie"
    LOC_PATH = "path"
    LOC_QUERY = "query"
    LOC_BODY = "body"

    # The token is missing from the request headers (403).
    ERR_VALUE_REQUIRED = "token_missing"

    # The token has expired and is no longer valid (403).
    ERR_TOKEN_EXPIRED = "token_expired"

    # The token is invalid and cannot be processed (403).
    ERR_TOKEN_INVALID = "token_invalid"

    # The token contains an invalid token identifier (403).
    ERR_TOKEN_REJECTED = "token_rejected"

    # The user is deleted or could not be found (403).
    ERR_TOKEN_ORPHANED = "token_orphaned"

    # The user is inactive and cannot access the resource (403).
    ERR_USER_INACTIVE = "user_inactive"

    # The user is temporarily suspended; try again later (403).
    ERR_USER_SUSPENDED = "user_suspended"

    # The user role is insufficient for this action (403).
    ERR_USER_REJECTED = "user_rejected"

    # The user cannot perform this action on the resource (403).
    ERR_RESOURCE_FORBIDDEN = "resource_forbidden"

    # The requested resource could not be found (404).
    ERR_RESOURCE_NOT_FOUND = "resource_not_found"

    # The resource that is being accessed is locked (423).
    ERR_RESOURCE_LOCKED = "resource_locked"

    # The value provided is empty (422).
    ERR_VALUE_EMPTY = "value_empty"

    # The value provided is invalid (422).
    ERR_VALUE_INVALID = "value_invalid"

    # The value provided already exists (422).
    ERR_VALUE_DUPLICATED = "value_duplicated"

    # The file MIME type is not supported for the operation (422).
    ERR_MIMETYPE_UNSUPPORTED = "mimetype_unsupported"

    # The value provided was rejected due to constraints (422).
    # ERR_VALUE_REJECTED = "value_rejected"

    # The value required for the operation is missing (422).
    # ERR_VALUE_REQUIRED = "value_required"

    def __init__(self, loc: list, error_input: str, error_type: str,
                 status_code: int):
        """
        Initializes the exception with detailed error information,
        including the location of the error, the input that caused it,
        the type of the error, and the HTTP status code.
        """
        detail = [{"loc": loc, "input": error_input, "type": error_type}]
        super().__init__(status_code=status_code, detail=detail)
