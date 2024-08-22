from fastapi import HTTPException, status
import enum


class Msg(enum.Enum):
    SERVER_ERROR = "Internal server error."
    BAD_REQUEST = "Bad request."

    USER_TOKEN_EMPTY = "User token is missing or empty."
    USER_TOKEN_EXPIRED = "User token has already expired."
    USER_TOKEN_INVALID = "User token has invalid format."
    USER_TOKEN_ORPHANED = "User token contains invalid user."
    USER_TOKEN_INACTIVE = "User token contains inactive user."
    USER_TOKEN_DECLINED = "User token contains invalid token identifier."
    USER_TOKEN_DENIED = "User token does not have sufficient role."

    USER_LOGIN_EXISTS = "User login already exists."
    USER_LOGIN_INACTIVE = "User is inactive."
    USER_LOGIN_SUSPENDED = "User is temporarily suspended."
    USER_LOGIN_DENIED = "User login denied because password is not accepted."
    USER_PASSWORD_INVALID = "User password is invalid."
    USER_PASSWORD_UNACCEPTED = "User password is not accepted."
    USER_TOTP_INVALID = "User one-time password is invalid."

    COLLECTION_EXISTS = "Collection already exists."
    COLLECTION_NOT_FOUND = "Collection not found."
    COLLECTION_LOCKED = "Collection locked."


"""
This module defines a custom HTTP exception class E for detailed error
reporting. It allows specifying the location of the error, the input
that caused it, and the type of the error, along with an optional HTTP
status code. This facilitates more informative error responses, aiding
in debugging and providing clearer feedback to users.
"""

E_LOC = "loc"
E_INPUT = "input"
E_TYPE = "type"


class E(HTTPException):
    """
    Custom HTTP exception class for detailed error reporting, allowing
    specification of error location, input, and type, with an optional
    HTTP status code. This class helps to provide more granular error
    information in responses, useful for debugging and user feedback.
    """

    # Token is missing or empty.
    E401_TOKEN_MISSING = "token_missing"

    # Token has already expired.
    E401_TOKEN_EXPIRED = "token_expired"

    # Token has invalid format.
    E401_TOKEN_INVALID = "token_invalid"

    # Token contains invalid JTI.
    E401_TOKEN_DECLINED = "token_declined"

    E403_USER_NOT_FOUND = "user_not_found"
    E403_USER_INACTIVE = "user_inactive"
    E403_USER_SUSPENDED = "user_suspended"

    # User declined because the role is insufficient.
    E403_USER_DECLINED = "user_declined"

    E404_ENTITY_NOT_FOUND = "entity_not_found"

    E422_VALUE_INVALID = "value_invalid"
    E422_VALUE_EXISTS = "value_exists"
    E422_VALUE_DECLINED = "value_declined"

    E423_ENTITY_LOCKED = "entity_locked"

    def __init__(self, loc: str, error_input: str, error_type: str,
                 status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        """
        Initializes the exception with detailed error information,
        including the location of the error, the input that caused it,
        and the type of the error, along with an optional HTTP status
        code, defaulting to 422 Unprocessable Entity.
        """
        detail = [{E_LOC: [loc], E_INPUT: error_input, E_TYPE: error_type}]
        super().__init__(status_code=status_code, detail=detail)
