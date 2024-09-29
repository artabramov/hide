"""
The module defines Pydantic schemas for managing mediafiles. Includes
schemas for inserting, selecting, updating, deleting, and listing
mediafiles.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.user_schemas import UserSelectResponse
from app.schemas.revision_schemas import RevisionSelectResponse
from app.validators.mediafile_validators import (
    validate_mediafile_summary, validate_mediafile_name, validate_tags)


class MediafileUploadResponse(BaseModel):
    mediafile_id: int
    revision_id: int


class MediafileReplaceResponse(BaseModel):
    mediafile_id: int
    revision_id: int


class MediafileSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a mediafile entity.
    Includes the mediafile ID, creation and update dates, user ID,
    collection ID, mediafile name, summary, size, and various counts
    such as revisions, comments, downloads, and favorites. Also includes
    the mediafile tags and the latest revision details.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    collection_id: Optional[int]

    mediafile_name: str
    mediafile_summary: Optional[str] = None
    comments_count: int
    revisions_count: int
    revisions_size: int
    downloads_count: int

    mediafile_tags: list
    mediafile_user: UserSelectResponse
    latest_revision: RevisionSelectResponse


class MediafileUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update an existing mediafile entity.
    Requires the mediafile ID and collection ID to be specified, and
    optionally the mediafile name, summary, and tags.
    """
    collection_id: Optional[int] = None
    mediafile_name: str = Field(..., min_length=1, max_length=256)
    mediafile_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)

    @field_validator("mediafile_summary", mode="before")
    def validate_mediafile_summary(cls, mediafile_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_mediafile_summary(mediafile_summary)

    @field_validator("mediafile_name", mode="before")
    def validate_mediafile_name(cls, mediafile_name: str) -> str:
        return validate_mediafile_name(mediafile_name)

    @field_validator("tags", mode="before")
    def validate_tags(cls, tags: str = None) -> Union[str, None]:
        return validate_tags(tags)


class MediafileUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a mediafile entity.
    Includes the ID assigned to the updated mediafile.
    """
    mediafile_id: int
    revision_id: int


class MediafileDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after updating a mediafile entity.
    Includes the ID assigned to the deleted mediafile.
    """
    mediafile_id: int


class MediafileListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of mediafile entities. Requires
    pagination options with offset and limit, ordering criteria, and
    optional filters for mediafile name and tag value.
    """
    collection_id__eq: Optional[int] = None
    mediafile_name__ilike: Optional[str] = None
    comments_count__ge: Optional[int] = None
    comments_count__le: Optional[int] = None
    revisions_count__ge: Optional[int] = None
    revisions_count__le: Optional[int] = None
    revisions_size__ge: Optional[int] = None
    revisions_size__le: Optional[int] = None
    downloads_count__ge: Optional[int] = None
    downloads_count__le: Optional[int] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_id", "mediafile_name", "comments_count",
                      "revisions_count", "revisions_size", "downloads_count"]
    order: Literal["asc", "desc", "rand"]


class MediafileListResponse(BaseModel):
    """
    Pydantic schema for the response when listing mediafile entities.
    Includes a list of mediafile entities and the total count of
    mediafile that match the request criteria.
    """
    mediafiles: List[MediafileSelectResponse]
    mediafiles_count: int
