from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.config import get_config

cfg = get_config()


def validate_collection_name(collection_name: str) -> str:
    """
    Ensure the collection name is at least 2 characters long after
    stripping extra spaces.
    """
    if len(collection_name.strip()) < 2:
        raise ValueError
    return collection_name.strip()


def validate_collection_summary(collection_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strip extra spaces from the collection summary if provided or None
    if not.
    """
    return collection_summary.strip() if collection_summary else None


class CollectionInsertRequest(BaseModel):
    """Pydantic schema for collection insertion request."""
    is_locked: bool
    collection_name: str = Field(..., min_length=2, max_length=128)
    collection_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("collection_name", mode="before")
    def validate_collection_name(cls, collection_name: str) -> str:
        """Normalize and validate the collection name."""
        return validate_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        """Normalize and validate the collection."""
        return validate_collection_summary(collection_summary)


class CollectionInsertResponse(BaseModel):
    """Pydantic schema for collection insertion response."""
    collection_id: int


class CollectionSelectRequest(BaseModel):
    """Pydantic schema for collection selection request."""
    collection_id: int


class CollectionSelectResponse(BaseModel):
    """Pydantic schema for collection selection response."""
    id: int
    created_date: int
    updated_date: int
    user_id: int
    is_locked: bool
    collection_name: str
    collection_summary: Optional[str]
    documents_count: int
    documents_size: int


class CollectionUpdateRequest(BaseModel):
    """Pydantic schema for collection updation request."""
    collection_id: int
    is_locked: bool
    collection_name: str = Field(..., min_length=2, max_length=128)
    collection_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("collection_name", mode="before")
    def validate_collection_name(cls, collection_name: str) -> str:
        """Normalize and validate the collection name."""
        return validate_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        """Normalize and validate the collection."""
        return validate_collection_summary(collection_summary)


class CollectionUpdateResponse(BaseModel):
    """Pydantic schema for collection updation response."""
    collection_id: int


class CollectionDeleteRequest(BaseModel):
    """Pydantic schema for collection deletion request."""
    collection_id: int


class CollectionDeleteResponse(BaseModel):
    """Pydantic schema for collection deletion response."""
    collection_id: int


class CollectionsListRequest(BaseModel):
    """Pydantic schema for collections list selection request."""
    collection_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_name", "documents_count",
                      "documents_size"]
    order: Literal["asc", "desc"]


class CollectionsListResponse(BaseModel):
    """Pydantic schema for collections list selection response."""
    collections: List[CollectionSelectResponse]
    collections_count: int
