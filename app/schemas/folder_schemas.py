from pydantic import BaseModel
from pydantic import SecretStr
# from fastapi import Query
from typing import Optional, Literal
# from app.models.user_models import UserRole
from pydantic import field_validator, Field
from app.config import get_config

cfg = get_config()


class FolderInsertRequest(BaseModel):
    is_locked: bool
    album_name: str = Field(..., min_length=2, max_length=128)
    album_summary: Optional[str] = Field(..., max_length=255, default="")

    # @field_validator("user_login", mode="before")
    # def validate_user_login(cls, user_login: str) -> str:
    #     return user_login.strip().lower()

    # @field_validator("user_password", mode="before")
    # def validate_user_password(cls, user_password: SecretStr) -> SecretStr:
    #     if len(user_password.get_secret_value().strip()) < 6:
    #         raise ValueError
    #     return user_password

    # @field_validator("first_name", mode="before")
    # def validate_first_name(cls, first_name: str) -> str:
    #     if len(first_name.strip()) < 2:
    #         raise ValueError
    #     return first_name

    # @field_validator("last_name", mode="before")
    # def validate_last_name(cls, last_name: str) -> str:
    #     if len(last_name.strip()) < 2:
    #         raise ValueError
    #     return last_name


class FolderInsertResponse(BaseModel):
    folder_id: int
