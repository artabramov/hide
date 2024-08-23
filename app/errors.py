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

    _LOC = "loc"
    _INPUT = "input"
    _TYPE = "type"

    # The token is missing from the request headers (401).
    TOKEN_MISSING = "token_missing"

    # The token has expired and is no longer valid (401).
    TOKEN_EXPIRED = "token_expired"

    # The token is invalid and cannot be processed (401).
    TOKEN_INVALID = "token_invalid"

    # The token contains an invalid token identifier (401).
    TOKEN_REJECTED = "token_rejected"

    # The user is deleted or could not be found (401).
    USER_NOT_FOUND = "user_not_found"

    # The user is inactive and cannot access the resource (401).
    USER_INACTIVE = "user_inactive"

    # The user is temporarily suspended; try again later (401).
    USER_SUSPENDED = "user_suspended"

    # The user role is insufficient for this action (401).
    ROLE_REJECTED = "role_rejected"

    # The user cannot perform this action on the resource (403).
    RESOURCE_FORBIDDEN = "resource_forbidden"

    # The requested resource could not be found (404).
    RESOURCE_NOT_FOUND = "resource_not_found"

    # The resource that is being accessed is locked (423).
    RESOURCE_LOCKED = "resource_locked"

    # The value provided already exists (422).
    VALUE_DUPLICATED = "value_duplicated"

    # The value provided is invalid (422).
    VALUE_INVALID = "value_invalid"

    # The file MIME type is unsupported (422).
    MIMETYPE_UNSUPPORTED = "mimetype_unsupported"

    # The value provided is empty (422).
    # VALUE_EMPTY = "value_empty"

    # The value provided was rejected due to constraints (422).
    # VALUE_REJECTED = "value_rejected"

    # The value required for the operation is missing (422).
    # VALUE_REQUIRED = "value_required"

    def __init__(self, loc: str, error_input: str, error_type: str,
                 status_code: int):
        """
        Initializes the exception with detailed error information,
        including the location of the error, the input that caused it,
        the type of the error, and the HTTP status code.
        """
        detail = [{E._LOC: [loc], E._INPUT: error_input, E._TYPE: error_type}]
        super().__init__(status_code=status_code, detail=detail)
