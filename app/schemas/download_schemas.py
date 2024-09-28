"""
The module defines Pydantic schemas for managing downloads. Includes
schemas for selecting and listing downloads.
"""

from typing import Literal, List
from pydantic import BaseModel, Field
from app.config import get_config
from app.schemas.user_schemas import UserSelectResponse

cfg = get_config()


class DownloadSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a download entity.
    Includes the download ID, creation date, user ID, mediafile ID, and
    details of the user who performed the download.
    """
    id: int
    created_date: int
    user_id: int
    mediafile_id: int
    download_user: UserSelectResponse


class DownloadListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of download entities. Requires
    pagination options with offset and limit, and ordering criteria, and
    optionally the mediafile ID.
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class DownloadListResponse(BaseModel):
    """
    Pydantic schema for the response when listing download entities.
    Includes a list of download entities and the total count of
    downloads that match the request criteria.
    """
    downloads: List[DownloadSelectResponse]
    downloads_count: int
