from typing import Optional, Literal, List
from pydantic import BaseModel, SecretStr, Field, field_validator
from fastapi import File, UploadFile
from app.models.user_models import UserRole
from app.config import get_config

cfg = get_config()


def validate_user_login(user_login: str) -> str:
    """
    Normalize the user login by stripping leading/trailing whitespace
    and converting  it to lowercase.
    """
    return user_login.strip().lower()


def validate_user_password(user_password: SecretStr) -> SecretStr:
    """
    Validate the user password. The password must be at least
    6 characters long.
    """
    if len(user_password.get_secret_value().strip()) < 6:
        raise ValueError
    return user_password


def validate_first_name(first_name: str) -> str:
    """
    Validate the first name. The first name must be at least
    2 characters long.
    """
    if len(first_name.strip()) < 2:
        raise ValueError
    return first_name


def validate_last_name(last_name: str) -> str:
    """
    Validate the last name. The last name must be at least
    2 characters long.
    """
    if len(last_name.strip()) < 2:
        raise ValueError
    return last_name


def validate_user_totp(user_totp: str) -> str:
    """
    Validate that the user TOTP (Time-based One-Time Password)
    is numeric.
    """
    if not user_totp.isnumeric():
        raise ValueError
    return user_totp


class UserRegisterRequest(BaseModel):
    """Pydantic schema for user registration request."""
    user_login: str = Field(..., pattern=r"^[a-z0-9]{2,40}$")
    user_password: SecretStr = Field(..., min_length=6)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)
    user_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        """Normalize and validate the user login."""
        return validate_user_login(user_login)

    @field_validator("user_password", mode="before")
    def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
        """Validate the user password."""
        return validate_user_password(user_password)

    @field_validator("first_name", mode="before")
    def validate_first_name(cls, first_name: str) -> str:
        """Validate the first name."""
        return validate_first_name(first_name)

    @field_validator("last_name", mode="before")
    def validate_last_name(cls, last_name: str) -> str:
        """Validate the last name."""
        return validate_last_name(last_name)


class UserRegisterResponse(BaseModel):
    """Pydantic schema for user registration response."""
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32)
    mfa_url: str


class MFARequest(BaseModel):
    """Pydantic schema for MFA (Multi-Factor Authentication) request."""
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32,
                            pattern=r"^[A-Za-z0-9]+$")


class UserLoginRequest(BaseModel):
    """Pydantic schema for user login request."""
    user_login: str
    user_password: SecretStr

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        """Normalize and validate the user login."""
        return validate_user_login(user_login)

    @field_validator("user_password", mode="before")
    def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
        """Validate the user password."""
        return validate_user_password(user_password)


class UserLoginResponse(BaseModel):
    """Pydantic schema for user login response."""
    password_accepted: bool


class TokenSelectRequest(BaseModel):
    """Pydantic schema for token selection request."""
    user_login: str
    user_totp: str = Field(..., min_length=6, max_length=6)

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        """Normalize and validate the user login."""
        return validate_user_login(user_login)

    @field_validator("user_totp", mode="before")
    def validate_user_totp(cls, user_login: str) -> str:
        """Validate that the user TOTP."""
        return validate_user_totp(user_login)


class TokenSelectResponse(BaseModel):
    """Pydantic schema for token selection response."""
    user_token: str


class TokenDeleteRequest(BaseModel):
    """Pydantic schema for token deletion request."""
    pass


class TokenDeleteResponse(BaseModel):
    """Pydantic schema for token deletion response."""
    pass


class UserSelectRequest(BaseModel):
    """Pydantic schema for user selection request."""
    user_id: int


class UserSelectResponse(BaseModel):
    """Pydantic schema for user selection response."""
    id: int
    created_date: int
    updated_date: int
    user_role: UserRole
    is_active: bool
    user_login: str
    first_name: str
    last_name: str
    user_summary: Optional[str]
    userpic_url: Optional[str]


class UserUpdateRequest(BaseModel):
    """Pydantic schema for user updation request."""
    user_id: int
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)
    user_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("first_name", mode="before")
    def validate_first_name(cls, first_name: str) -> str:
        """Validate the first name."""
        return validate_first_name(first_name)

    @field_validator("last_name", mode="before")
    def validate_last_name(cls, last_name: str) -> str:
        """Validate the last name."""
        return validate_last_name(last_name)


class UserUpdateResponse(BaseModel):
    """Pydantic schema for user updation response."""
    user_id: int


class UserpicUploadRequest(BaseModel):
    """Pydantic schema for userpic uploading request."""
    user_id: int
    file: UploadFile = File(...)


class UserpicUploadResponse(BaseModel):
    """Pydantic schema for userpic uploading response."""
    user_id: int


class UserpicDeleteRequest(BaseModel):
    """Pydantic schema for userpic deletion request."""
    user_id: int


class UserpicDeleteResponse(BaseModel):
    """Pydantic schema for userpic deletion response."""
    user_id: int


class RoleUpdateRequest(BaseModel):
    """Pydantic schema for user role updation request."""
    user_id: int
    user_role: UserRole
    is_active: bool


class RoleUpdateResponse(BaseModel):
    """Pydantic schema for user role updation response."""
    user_id: int


class PasswordUpdateRequest(BaseModel):
    """Pydantic schema for user password updation request."""
    user_id: int
    current_password: SecretStr = Field(..., min_length=6)
    updated_password: SecretStr = Field(..., min_length=6)

    @field_validator("current_password", mode="before")
    def validate_current_password(cls, current_password: SecretStr) -> SecretStr:  # noqa E501
        """Validate current password."""
        return validate_user_password(current_password)

    @field_validator("updated_password", mode="before")
    def validate_updated_password(cls, updated_password: SecretStr) -> SecretStr:  # noqa E501
        """Validate updated password."""
        return validate_user_password(updated_password)


class PasswordUpdateResponse(BaseModel):
    """Pydantic schema for user password updation response."""
    user_id: int


class UsersListRequest(BaseModel):
    """Pydantic schema for users list selection request."""
    user_login__ilike: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "user_login", "first_name", "last_name"]
    order: Literal["asc", "desc"]


class UsersListResponse(BaseModel):
    """Pydantic schema for users list selection response."""
    users: List[UserSelectResponse]
    users_count: int
