from pydantic import BaseModel
from pydantic import SecretStr
# from fastapi import Query
# from typing import Optional, Literal
# from app.models.user_models import UserRole
from pydantic import field_validator, Field
from app.config import get_config

cfg = get_config()


class UserRegisterRequest(BaseModel):
    user_login: str = Field(..., pattern=r"^[a-z0-9]{2,40}$")
    user_password: SecretStr = Field(..., min_length=6)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)

    @field_validator("user_login", mode="before")
    def validate_user_login(cls, user_login: str) -> str:
        return user_login.strip().lower()

    @field_validator("user_password", mode="before")
    def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
        if not user_password.get_secret_value().strip():
            raise ValueError
        return user_password


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
