"""
The module defines Pydantic schemas for managing revisions. Includes
schemas for downloading, selecting, and listing revisions.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from app.schemas.user_schemas import UserSelectResponse


class RevisionDownloadRequest(BaseModel):
    """
    Pydantic schema for request to download a specific revision.
    Requires the revision ID to be specified.
    """
    revision_id: int


class RevisionSelectRequest(BaseModel):
    """
    Pydantic schema for request to retrieve a specific revision.
    Requires the revision ID to be specified.
    """
    revision_id: int


class RevisionSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a specific
    revision. Includes the revision ID, creation date, user ID,
    document ID, whether it is the latest revision, revision size,
    original filename, original file size, original file MIME type,
    optional thumbnail URL, downloads count, and details of the
    related user.
    """
    id: int
    created_date: int
    user_id: int
    document_id: int
    is_latest: bool
    revision_size: int
    original_filename: str
    original_size: int
    original_mimetype: str
    thumbnail_url: Optional[str] = None
    downloads_count: int
    revision_user: UserSelectResponse


class RevisionListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of revision entities. Includes
    optional filters for creation date, user ID, document ID, revision
    size, original file size, original filename, original MIME type,
    downloads count, pagination options with offset and limit, and
    ordering criteria.
    """
    created_date__ge: Optional[int] = None
    created_date__le: Optional[int] = None
    user_id__eq: Optional[int] = None
    document_id__eq: Optional[int] = None
    revision_size__ge: Optional[int] = None
    revision_size__le: Optional[int] = None
    original_size__ge: Optional[int] = None
    original_size__le: Optional[int] = None
    original_filename__ilike: Optional[str] = None
    original_mimetype__eq: Optional[str] = None
    downloads_count__ge: Optional[int] = None
    downloads_count__le: Optional[int] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "user_id", "document_id",
                      "revision_size", "original_size", "original_filename",
                      "original_mimetype", "downloads_count"]
    order: Literal["asc", "desc"]


class RevisionListResponse(BaseModel):
    """
    Pydantic schema for the response when listing revision entities.
    Includes a list of revision entities and the total count of
    revisions that match the request criteria.
    """
    revisions: List[RevisionSelectResponse]
    revisions_count: int
