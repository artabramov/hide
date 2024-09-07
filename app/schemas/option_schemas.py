"""
The module defines Pydantic schemas for managing option entities in the
application, including schemas for selecting, updating, deleting, and
listing options. It provides validation rules for each operation.
"""

from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.validators.option_validators import (
    validate_option_key, validate_option_value)


class OptionSelectRequest(BaseModel):
    """
    Pydantic schema for retrieving an option entity by its key. The
    schema validates that the option key corresponds to the required
    pattern.
    """
    option_key: str = Field(..., pattern=r"^[a-z0-9_-]{2,40}$")

    @field_validator("option_key", mode="before")
    def validate_option_key(cls, option_key: str) -> str:
        return validate_option_key(option_key)


class OptionSelectResponse(BaseModel):
    """
    Pydantic schema for the response when retrieving an option entity.
    The schema includes the ID, creation and last update dates, the
    option key, and value.
    """
    id: int
    created_date: int
    updated_date: int
    option_key: str
    option_value: str


class OptionUpdateRequest(BaseModel):
    """
    Pydantic schema for updating an option entity by its key. The schema
    validates the option key to ensure it matches the required pattern
    and the option value to ensure it does not exceed the maximum length.
    """
    option_key: str = Field(..., pattern=r"^[a-z0-9_-]{2,40}$")
    option_value: str = Field(..., max_length=512)

    @field_validator("option_key", mode="before")
    def validate_option_key(cls, option_key: str) -> str:
        return validate_option_key(option_key)

    @field_validator("option_value", mode="before")
    def validate_option_value(cls, option_value: str) -> str:
        return validate_option_value(option_value)


class OptionUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating an option entity.
    The schema includes the option key to confirm which option was
    updated.
    """
    option_key: str


class OptionDeleteRequest(BaseModel):
    """
    Pydantic schema for requesting the deletion of an option entity by
    its key. The schema validates the option key to ensure it matches
    the required pattern.
    """
    option_key: str = Field(..., pattern=r"^[a-z0-9_-]{2,40}$")

    @field_validator("option_key", mode="before")
    def validate_option_key(cls, option_key: str) -> str:
        return validate_option_key(option_key)


class OptionDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after requesting the deletion of
    an option entity. The schema includes the option key, which is None
    if the option was not found, and contains the key of the deleted
    option if the deletion was successful.
    """
    option_key: Optional[str] = None


class OptionListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of option entities with
    pagination and sorting. The schema allows specifying the starting
    offset, the limit, the field to sort by, and the sort order.
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "option_key"]
    order: Literal["asc", "desc"]


class OptionListResponse(BaseModel):
    """
    Pydantic schema for the response containing a list of option
    entities and a count of the total number of options available.
    """
    options: List[OptionSelectResponse]
    options_count: int
