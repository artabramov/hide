"""
This module defines Pydantic schemas for managing and retrieving
download-related data. It includes schemas for selecting individual
downloads, listing downloads with pagination and sorting options, and
detailed information about each download. These schemas ensure data
validation and structure for API requests and responses related to
document downloads.
"""

from typing import Literal, List
from pydantic import BaseModel, Field
from app.config import get_config
from app.schemas.user_schemas import UserSelectResponse

cfg = get_config()


class DownloadSelectRequest(BaseModel):
    """
    Pydantic schema for selecting a specific download by its ID.
    """
    download_id: int


class DownloadSelectResponse(BaseModel):
    """
    Pydantic schema representing the details of a download, including
    the ID, creation date, user ID, document ID, and a nested user
    response schema for the download's user.
    """
    id: int
    created_date: int
    user_id: int
    document_id: int
    download_user: UserSelectResponse


class DownloadListRequest(BaseModel):
    """
    Pydantic schema for listing downloads with query parameters,
    including filtering by document ID, pagination through offset and
    limit, and sorting options by creation date or ID in ascending or
    descending order.
    """
    document_id__eq: int
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class DownloadListResponse(BaseModel):
    """
    Pydantic schema for the response of listing downloads, containing a
    list of download details and the total count of downloads.
    """
    downloads: List[DownloadSelectResponse]
    downloads_count: int
