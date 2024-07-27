from fastapi import HTTPException, status
import enum


class Msg(enum.Enum):
    SERVER_ERROR = "Internal server error."
    BAD_REQUEST = "Bad request."

    USER_TOKEN_EMPTY = "User token is missing or empty."
    USER_TOKEN_EXPIRED = "User token has already expired."
    USER_TOKEN_INVALID = "User token has invalid format."
    USER_TOKEN_ORPHANED = "User token contains invalid user data."
    USER_TOKEN_DECLINED = "User token contains invalid identifier."
    USER_TOKEN_DENIED = "User token does not have sufficient role."

    USER_LOGIN_EXISTS = "User login already exists."
    USER_LOGIN_INACTIVE = "User is inactive."
    USER_LOGIN_SUSPENDED = "User is temporarily suspended."
    USER_LOGIN_DENIED = "User login denied because password is not accepted."
    USER_PASSWORD_INVALID = "User password is invalid."
    USER_PASSWORD_UNACCEPTED = "User password is not accepted."
    USER_TOTP_INVALID = "User one-time password is invalid."


class E(HTTPException):

    def __init__(self, loc: str, error_input: str, msg: Msg,
                 status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):

        detail = [{"loc": [loc], "input": error_input,
                   "type": msg.name.lower(), "msg": msg.value}]
        super().__init__(status_code=status_code, detail=detail)
