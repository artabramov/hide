from pydantic import BaseModel
from typing import Optional
from pydantic import Field, field_validator
from app.config import get_config

cfg = get_config()


def _validate_album_name(album_name: str) -> str:
    if len(album_name.strip()) < 2:
        raise ValueError
    return album_name.strip()


def _validate_album_summary(album_summary: str = None) -> str | None:
    return album_summary.strip() if album_summary else None


class AlbumInsertRequest(BaseModel):
    is_locked: bool
    album_name: str = Field(..., min_length=2, max_length=128)
    album_summary: Optional[str] = Field(max_length=255, default=None)

    @field_validator("album_name", mode="before")
    def validate_album_name(cls, album_name: str) -> str:
        return _validate_album_name(album_name)

    @field_validator("album_summary", mode="before")
    def validate_album_summary(cls, album_summary: str = None) -> str | None:
        return _validate_album_summary(album_summary)


class AlbumInsertResponse(BaseModel):
    album_id: int


class AlbumSelectRequest(BaseModel):
    album_id: int


class AlbumSelectResponse(BaseModel):
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
    album_id: int
    is_locked: bool
    album_name: str = Field(..., min_length=2, max_length=128)
    album_summary: Optional[str] = Field(max_length=255, default=None)


class AlbumUpdateResponse(BaseModel):
    album_id: int
