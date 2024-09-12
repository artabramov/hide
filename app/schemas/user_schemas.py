"""
The module defines Pydantic schemas for managing users. Includes schemas
for registration, login, multi-factor authentication, token retrieval
and invalidation, role and profile updating, userpic management,
password changes, and user listing.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, SecretStr, Field, field_validator
from fastapi import File, UploadFile
from app.models.user_model import UserRole
from app.validators.user_validators import (
    validate_user_login, validate_user_password, validate_first_name,
    validate_last_name, validate_user_totp, validate_token_exp,
    validate_user_signature, validate_user_contacts)


class UserRegisterRequest(BaseModel):
    """
    Pydantic schema for request to register a new user. Requires the
    user login, password, first name, and last name to be specified.
    Optionally includes a user signature and user contacts.
    """
    user_login: str = Field(..., pattern=r"^[a-zA-Z0-9]{2,40}$")
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

    @field_validator("user_signature", mode="before")
    def validate_user_signature(cls, user_signature: str = None) -> Union[str, None]:  # noqa E501
        return validate_user_signature(user_signature)

    @field_validator("user_contacts", mode="before")
    def validate_user_contacts(cls, user_contacts: str = None) -> Union[str, None]:  # noqa E501
        return validate_user_contacts(user_contacts)


class UserRegisterResponse(BaseModel):
    """
    Pydantic schema for the response after registering a new user.
    Includes the user ID, MFA secret, and an URL for the MFA QR code
    image.
    """
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32)
    mfa_url: str


class MFARequest(BaseModel):
    """
    Pydantic schema for request the MFA QR code image. Requires the user
    ID and MFA secret to be specified.
    """
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32,
                            pattern=r"^[A-Za-z0-9]+$")


class UserLoginRequest(BaseModel):
    """
    Pydantic schema for request to authenticate a user. Requires the
    user login and password to be specified.
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
    Pydantic schema for response after attempting user login. Includes
    a boolean indicating whether the password was accepted.
    """
    password_accepted: bool


class TokenRetrieveRequest(BaseModel):
    """
    Pydantic schema for request to retrieve a token. Requires the user
    login and TOTP code to be specified, with an optional token
    expiration parameter.
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
    Pydantic schema for the response after retrieving a JWT token.
    Includes the JWT token assigned to the user.
    """
    user_token: str


class UserSelectRequest(BaseModel):
    """
    Pydantic schema for request to retrieve a user entity. Requires
    the user ID to be specified.
    """
    user_id: int


class UserSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a user entity.
    Includes the user ID, creation and update dates, last log in date,
    user role, active status, user login, first and last name, signature,
    contacts, and userpic URL.
    """
    id: int
    created_date: int
    updated_date: int
    last_login_date: int
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
    Pydantic schema for request to update a user entity. Requires the
    user ID, first and last name, and optionally user signature and
    user contacts.
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

    @field_validator("user_signature", mode="before")
    def validate_user_signature(cls, user_signature: str = None) -> Union[str, None]:  # noqa E501
        return validate_user_signature(user_signature)

    @field_validator("user_contacts", mode="before")
    def validate_user_contacts(cls, user_contacts: str = None) -> Union[str, None]:  # noqa E501
        return validate_user_contacts(user_contacts)


class UserUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a user entity.
    Includes the ID assigned to the updated user.
    """
    user_id: int


class UserDeleteRequest(BaseModel):
    """
    Pydantic schema for request to delete a user entity. Requires
    the user ID to be specified.
    """
    user_id: int


class UserDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a user entity.
    Includes the ID assigned to the deleted user.
    """
    user_id: int


class UserpicUploadRequest(BaseModel):
    """
    Pydantic schema for request to upload a user profile picture.
    Requires the user ID and the image file to be uploaded.
    """
    user_id: int
    file: UploadFile = File(...)


class UserpicUploadResponse(BaseModel):
    """
    Pydantic schema for the response after uploading a user profile
    picture. Includes the user ID associated with the uploaded picture.
    """
    user_id: int


class UserpicDeleteRequest(BaseModel):
    """
    Pydantic schema for request to delete a user profile picture.
    Requires the user ID to be specified.
    """
    user_id: int


class UserpicDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a user profile
    picture. Includes the user ID of the profile picture that was
    deleted.
    """
    user_id: int


class RoleUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update a user's role and active
    status. Requires the user ID, new user role, and active status
    to be specified.
    """
    user_id: int
    user_role: UserRole
    is_active: bool


class RoleUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a user's role and
    active status. Includes the user ID of the updated user.
    """
    user_id: int


class PasswordUpdateRequest(BaseModel):
    """
    Pydantic schema for requesting a password update for a user.
    Requires the user ID, current password, and the new updated
    password to be specified.
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
    Pydantic schema for the response after updating a user's password.
    Includes the user ID of the user whose password was updated.
    """
    user_id: int


class UserListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of user entities. Requires
    pagination options with offset and limit, ordering criteria, and
    optional filters for user login, first name, and last name.
    """
    is_active__eq: Optional[bool] = None
    user_role__eq: Optional[UserRole] = None
    user_login__ilike: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "last_login_date",
                      "user_role", "is_active", "user_login", "first_name",
                      "last_name"]
    order: Literal["asc", "desc"]


class UserListResponse(BaseModel):
    """
    Pydantic schema for the response when listing user entities.
    Includes a list of user entities and the total count of users that
    match the request criteria.
    """
    users: List[UserSelectResponse]
    users_count: int
