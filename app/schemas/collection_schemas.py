"""
This module defines Pydantic schemas for handling various operations
related to collections. Schemas include requests and responses for
inserting, selecting, updating, deleting, and listing collections,
with validation for fields such as collection names and summaries.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.config import get_config
from app.schemas.user_schemas import UserSelectResponse
from app.validators.collection_validators import (
    validate_collection_name, validate_collection_summary)

cfg = get_config()


class CollectionInsertRequest(BaseModel):
    """
    Pydantic schema for requesting the insertion of a new collection.
    Includes attributes to define the collection's locked status, name,
    and summary, with validation to ensure the name meets length
    requirements.
    """
    is_locked: bool
    collection_name: str = Field(..., min_length=2, max_length=128)
    collection_summary: Optional[str] = Field(min_length=2, max_length=512,
                                              default=None)

    @field_validator("collection_name", mode="before")
    def validate_collection_name(cls, collection_name: str) -> str:
        """Validate the collection name."""
        return validate_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        """Validate the collection summary."""
        return validate_collection_summary(collection_summary)


class CollectionInsertResponse(BaseModel):
    """
    Pydantic schema for the response after inserting a new collection.
    Contains the unique identifier of the newly created collection.
    """
    collection_id: int


class CollectionSelectRequest(BaseModel):
    """
    Pydantic schema for requesting a specific collection by its ID.
    Contains the unique identifier of the collection to be selected.
    """
    collection_id: int


class CollectionSelectResponse(BaseModel):
    """
    Pydantic schema for the response after selecting a collection.
    Provides details about the collection including its ID, creation and
    update dates, user ID, locked status, name, summary, document count,
    document size, and user details.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    is_locked: bool
    collection_name: str
    collection_summary: Optional[str] = None
    documents_count: int
    revisions_count: int
    revisions_size: int
    originals_count: int
    collection_user: UserSelectResponse


class CollectionUpdateRequest(BaseModel):
    """
    Pydantic schema for requesting the update of an existing collection.
    Includes attributes for updating the collection's ID, locked status,
    name, and summary with validation for name length.
    """
    collection_id: int
    is_locked: bool
    collection_name: str = Field(..., min_length=2, max_length=128)
    collection_summary: Optional[str] = Field(min_length=2, max_length=512,
                                              default=None)

    @field_validator("collection_name", mode="before")
    def validate_collection_name(cls, collection_name: str) -> str:
        """Normalize and validate the collection name."""
        return validate_collection_name(collection_name)

    @field_validator("collection_summary", mode="before")
    def validate_collection_summary(cls, collection_summary: str = None) -> Union[str, None]:  # noqa E501
        """Normalize and validate the collection."""
        return validate_collection_summary(collection_summary)


class CollectionUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a collection.
    Contains the unique identifier of the updated collection.
    """
    collection_id: int


class CollectionDeleteRequest(BaseModel):
    """
    Pydantic schema for requesting the deletion of a collection by its
    ID. Contains the unique identifier of the collection to be deleted.
    """
    collection_id: int


class CollectionDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a collection.
    Contains the unique identifier of the deleted collection.
    """
    collection_id: int


class CollectionsListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of collections with optional
    filters for name, pagination through offset and limit, and sorting
    options by various attributes and order.
    """
    collection_name__ilike: Optional[str] = None
    is_locked__eq: Optional[bool] = None
    documents_count__ge: Optional[int] = None
    documents_count__le: Optional[int] = None
    documents_size__ge: Optional[int] = None
    documents_size__le: Optional[int] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_name", "documents_count", "documents_size",
                      "revisions_count", "revisions_size"]
    order: Literal["asc", "desc"]


class CollectionsListResponse(BaseModel):
    """
    Pydantic schema for the response containing a list of collections
    and the total count of collections that match the request criteria.
    """
    collections: List[CollectionSelectResponse]
    collections_count: int
