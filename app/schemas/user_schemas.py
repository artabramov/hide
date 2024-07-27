from pydantic import BaseModel


"""Pydantic schemas for user model."""

from pydantic import SecretStr
# from fastapi import Query
# from typing import Optional, Literal
# from app.models.user_models import UserRole
from pydantic import field_validator, Field
from app.config import get_config

cfg = get_config()


class UserRegisterRequest(BaseModel):
    user_login: str = Field(..., min_length=2, max_length=40,
                            pattern=r"^[a-z0-9]+$")
    user_password: SecretStr = Field(..., min_length=6)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)

    @field_validator("user_login", mode="before")
    def _user_login(cls, user_login: str):
        return user_login.strip().lower()


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


class UserTokenRequest(BaseModel):
    """Pydantic schema for token selection request."""

    user_login: str
    user_totp: str = Field(..., min_length=6, max_length=6)


class UserTokenResponse(BaseModel):
    """Pydantic schema for token selection request."""

    user_token: str
