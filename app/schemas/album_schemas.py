from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.config import get_config

cfg = get_config()


def validate_album_name(album_name: str) -> str:
    """
    Ensure the album name is at least 2 characters long after stripping
    extra spaces.
    """
    if len(album_name.strip()) < 2:
        raise ValueError
    return album_name.strip()


def validate_album_summary(album_summary: str = None) -> Union[str, None]:
    """
    Strip extra spaces from the album summary if provided; return None
    if no summary is given.
    """
    return album_summary.strip() if album_summary else None


class AlbumInsertRequest(BaseModel):
    """Pydantic schema for album insertion request."""
    is_locked: bool
    album_name: str = Field(..., min_length=2, max_length=128)
    album_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("album_name", mode="before")
    def validate_album_name(cls, album_name: str) -> str:
        """Normalize and validate the album name."""
        return validate_album_name(album_name)

    @field_validator("album_summary", mode="before")
    def validate_album_summary(cls, album_summary: str = None) -> Union[str, None]:  # noqa E501
        """Normalize and validate the album."""
        return validate_album_summary(album_summary)


class AlbumInsertResponse(BaseModel):
    """Pydantic schema for album insertion response."""
    album_id: int


class AlbumSelectRequest(BaseModel):
    """Pydantic schema for album selection request."""
    album_id: int


class AlbumSelectResponse(BaseModel):
    """Pydantic schema for album selection response."""
    id: int
    created_date: int
    updated_date: int
    user_id: int
    is_locked: bool
    album_name: str
    album_summary: Optional[str]
    posts_count: int
    posts_size: int


class AlbumUpdateRequest(BaseModel):
    """Pydantic schema for album updation request."""
    album_id: int
    is_locked: bool
    album_name: str = Field(..., min_length=2, max_length=128)
    album_summary: Optional[str] = Field(max_length=512, default=None)

    @field_validator("album_name", mode="before")
    def validate_album_name(cls, album_name: str) -> str:
        """Normalize and validate the album name."""
        return validate_album_name(album_name)

    @field_validator("album_summary", mode="before")
    def validate_album_summary(cls, album_summary: str = None) -> Union[str, None]:  # noqa E501
        """Normalize and validate the album."""
        return validate_album_summary(album_summary)


class AlbumUpdateResponse(BaseModel):
    """Pydantic schema for album updation response."""
    album_id: int


class AlbumDeleteRequest(BaseModel):
    """Pydantic schema for album deletion request."""
    album_id: int


class AlbumDeleteResponse(BaseModel):
    """Pydantic schema for album deletion response."""
    album_id: int


class AlbumsListRequest(BaseModel):
    """Pydantic schema for albums list selection request."""
    album_name__ilike: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "album_name", "posts_count", "posts_size"]
    order: Literal["asc", "desc"]


class AlbumsListResponse(BaseModel):
    """Pydantic schema for albums list selection response."""
    albums: List[AlbumSelectResponse]
    albums_count: int
