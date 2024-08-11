from pydantic import BaseModel
from pydantic import SecretStr
# from fastapi import Query
from typing import Optional
# from app.models.user_models import UserRole
from pydantic import Field, field_validator
from app.config import get_config
from fastapi import File, UploadFile
from app.models.user_models import UserRole


cfg = get_config()


class UserRegisterRequest(BaseModel):
    user_login: str = Field(..., pattern=r"^[a-z0-9]{2,40}$")
    user_password: SecretStr = Field(..., min_length=6)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)
    user_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        return user_login.strip().lower()

    @field_validator("user_password", mode="before")
    def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
        if len(user_password.get_secret_value().strip()) < 6:
            raise ValueError
        return user_password

    @field_validator("first_name", mode="before")
    def validate_first_name(cls, first_name: str) -> str:
        if len(first_name.strip()) < 2:
            raise ValueError
        return first_name

    @field_validator("last_name", mode="before")
    def validate_last_name(cls, last_name: str) -> str:
        if len(last_name.strip()) < 2:
            raise ValueError
        return last_name


class UserRegisterResponse(BaseModel):
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32)
    mfa_url: str


class MFARequest(BaseModel):
    user_id: int
    mfa_secret: str = Field(..., min_length=32, max_length=32,
                            pattern=r"^[A-Za-z0-9]+$")


class UserLoginRequest(BaseModel):
    """Pydantic schema for user login."""
    user_login: str
    user_password: SecretStr


class UserLoginResponse(BaseModel):
    """Pydantic schema for user login."""
    password_accepted: bool


class TokenSelectRequest(BaseModel):
    user_login: str
    user_totp: str = Field(..., min_length=6, max_length=6)


class TokenSelectResponse(BaseModel):
    user_token: str


class TokenDeleteRequest(BaseModel):
    pass


class TokenDeleteResponse(BaseModel):
    pass


class UserSelectRequest(BaseModel):
    user_id: int


class UserSelectResponse(BaseModel):
    user: dict


class UserUpdateRequest(BaseModel):
    user_id: int
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)
    user_summary: Optional[str] = Field(max_length=512, default=None)


class UserUpdateResponse(BaseModel):
    user_id: int


class UserpicUploadRequest(BaseModel):
    user_id: int
    file: UploadFile = File(...)


class UserpicUploadResponse(BaseModel):
    user_id: int


class UserpicDeleteRequest(BaseModel):
    user_id: int


class UserpicDeleteResponse(BaseModel):
    user_id: int


class RoleUpdateRequest(BaseModel):
    user_id: int
    user_role: UserRole
    is_active: bool


class RoleUpdateResponse(BaseModel):
    user_id: int


class PasswordUpdateRequest(BaseModel):
    user_id: int
    user_password: SecretStr = Field(..., min_length=6)


class PasswordUpdateResponse(BaseModel):
    user_id: int
