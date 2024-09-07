from typing import Optional, Literal, List
from pydantic import BaseModel, SecretStr, Field, field_validator
from fastapi import File, UploadFile
from app.models.user_models import UserRole
from app.validators.user_validators import (
    validate_user_login, validate_user_password, validate_first_name,
    validate_last_name, validate_user_totp, validate_token_exp)


class UserRegisterRequest(BaseModel):
    """
    Pydantic schema for user registration request, including validation
    for user login, password, first name, last name, and optional fields
    for user signature and contacts.
    """
    user_login: str = Field(..., pattern=r"^[a-z0-9]{2,40}$")
    user_password: SecretStr = Field(..., min_length=6)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)
    user_signature: Optional[str] = Field(max_length=40, default=None)
    user_contacts: Optional[str] = Field(max_length=512, default=None)

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        return validate_user_login(user_login)

    @field_validator("user_password", mode="before")
    def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
        return validate_user_password(user_password)

    @field_validator("first_name", mode="before")
    def validate_first_name(cls, first_name: str) -> str:
        return validate_first_name(first_name)

    @field_validator("last_name", mode="before")
    def validate_last_name(cls, last_name: str) -> str:
        return validate_last_name(last_name)


class UserRegisterResponse(BaseModel):
    """
    Pydantic schema for the user registration response, including the
    user's ID, MFA secret, and a URL linking to the MFA QR code.
    """
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32)
    mfa_url: str


class MFARequest(BaseModel):
    """
    Pydantic schema for MFA (Multi-Factor Authentication) request,
    including the user's ID and the MFA secret.
    """
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32,
                            pattern=r"^[A-Za-z0-9]+$")


class UserLoginRequest(BaseModel):
    """
    Pydantic schema for user login request, including validation for
    user login and password.
    """
    user_login: str = Field(..., pattern=r"^[a-z0-9]{2,40}$")
    user_password: SecretStr = Field(..., min_length=6)

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        return validate_user_login(user_login)

    @field_validator("user_password", mode="before")
    def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
        return validate_user_password(user_password)


class UserLoginResponse(BaseModel):
    """
    Pydantic schema for the user login response, indicating whether
    the password was accepted.
    """
    password_accepted: bool


class TokenRetrieveRequest(BaseModel):
    """
    Pydantic schema for token retrieval request, including validation
    for the user login, TOTP (Time-based One-Time Password), and
    optional token expiration time.
    """
    user_login: str = Field(..., pattern=r"^[a-z0-9]{2,40}$")
    user_totp: str = Field(..., min_length=6, max_length=6)
    token_exp: Optional[int] = None

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        return validate_user_login(user_login)

    @field_validator("user_totp", mode="before")
    def validate_user_totp(cls, user_login: str) -> str:
        return validate_user_totp(user_login)

    @field_validator("token_exp", mode="before")
    def validate_token_exp(cls, token_exp: str = None) -> str:
        return validate_token_exp(token_exp)


class TokenRetrieveResponse(BaseModel):
    """
    Pydantic schema for the token retrieval response, providing the
    JWT (JSON Web Token) upon successful token selection.
    """
    user_token: str


class TokenInvalidateRequest(BaseModel):
    """
    Pydantic schema for token invalidation request. It does not require
    any additional fields.
    """
    pass


class TokenInvalidateResponse(BaseModel):
    """
    Pydantic schema for the token invalidation response. It does not
    include any additional fields.
    """
    pass


class UserSelectRequest(BaseModel):
    """
    Pydantic schema for the user selection request, including the
    user ID.
    """
    user_id: int


class UserSelectResponse(BaseModel):
    """
    Pydantic schema for the user selection response, providing details
    of the user. Includes fields for the user ID, creation date, last
    update date, last log in date, user role, activation status, user
    login, first and last name, and optional fields for user signature,
    contacts, and userpic URL.
    """
    id: int
    created_date: int
    updated_date: int
    logged_date: int
    user_role: UserRole
    is_active: bool
    user_login: str
    first_name: str
    last_name: str
    user_signature: Optional[str] = None
    user_contacts: Optional[str] = None
    userpic_url: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """
    Pydantic schema for user update requests. Includes the user ID,
    first name, last name, user  signature, and user contacts.
    """
    user_id: int
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)
    user_signature: Optional[str] = Field(max_length=40, default=None)
    user_contacts: Optional[str] = Field(max_length=512, default=None)

    @field_validator("first_name", mode="before")
    def validate_first_name(cls, first_name: str) -> str:
        return validate_first_name(first_name)

    @field_validator("last_name", mode="before")
    def validate_last_name(cls, last_name: str) -> str:
        return validate_last_name(last_name)


class UserUpdateResponse(BaseModel):
    """
    Pydantic schema for the response of a user update request. Includes
    the user ID of the updated user.
    """
    user_id: int


class UserpicUploadRequest(BaseModel):
    """
    Pydantic schema for the request to upload a userpic. Includes
    the user ID and the file to be uploaded.
    """
    user_id: int
    file: UploadFile = File(...)


class UserpicUploadResponse(BaseModel):
    """
    Pydantic schema for the response of a userpic upload request.
    Includes the user ID of the user whose userpic was uploaded.
    """
    user_id: int


class UserpicDeleteRequest(BaseModel):
    """
    Pydantic schema for the request to delete a userpic. Includes
    the user ID of the user whose userpic is to be deleted.
    """
    user_id: int


class UserpicDeleteResponse(BaseModel):
    """
    Pydantic schema for the response to a userpic deletion request.
    Includes the user ID of the user whose userpic was deleted.
    """
    user_id: int


class RoleUpdateRequest(BaseModel):
    """
    Pydantic schema for requesting an update to a user's role and
    activation status. Includes the user ID, the new role for the user,
    and the user's activation status.
    """
    user_id: int
    user_role: UserRole
    is_active: bool


class RoleUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a user's role.
    Includes the user ID of the updated user.
    """
    user_id: int


class PasswordUpdateRequest(BaseModel):
    """
    Pydantic schema for a request to update a user's password. Includes
    the user ID, current password, and the new password.
    """
    user_id: int
    current_password: SecretStr = Field(..., min_length=6)
    updated_password: SecretStr = Field(..., min_length=6)

    @field_validator("current_password", mode="before")
    def validate_current_password(cls, current_password: SecretStr) -> SecretStr:  # noqa E501
        return validate_user_password(current_password)

    @field_validator("updated_password", mode="before")
    def validate_updated_password(cls, updated_password: SecretStr) -> SecretStr:  # noqa E501
        return validate_user_password(updated_password)


class PasswordUpdateResponse(BaseModel):
    """
    Pydantic schema for the response to a user password update request.
    Includes the ID of the user whose password has been updated.
    """
    user_id: int


class UserListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of users. Includes optional
    filters for user login, first name, and last name, pagination and
    ordering parameters.
    """
    user_login__ilike: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "user_login", "first_name", "last_name"]
    order: Literal["asc", "desc"]


class UserListResponse(BaseModel):
    """
    Pydantic schema for the response of a user list selection request.
    Contains a list of user details and the total count of users.
    """
    users: List[UserSelectResponse]
    users_count: int
