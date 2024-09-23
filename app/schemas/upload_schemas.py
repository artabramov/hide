"""
The module defines Pydantic schemas for managing documents. Includes
schemas for inserting, selecting, updating, deleting, and listing
documents.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from app.schemas.user_schemas import UserSelectResponse


class UploadSelectResponse(BaseModel):
    id: int
    created_date: int
    user_id: int
    document_id: int
    is_latest: bool
    upload_size: int
    original_filename: str
    original_size: int
    original_mimetype: str
    thumbnail_url: Optional[str] = None
    downloads_count: int
    upload_user: UserSelectResponse


class UploadListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of upload entities. Includes
    optional filter for document ID and pagination options with offset
    and limit, and ordering criteria.
    """
    document_id__eq: Optional[int] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class UploadListResponse(BaseModel):
    """
    Pydantic schema for the response when listing upload entities.
    Includes a list of upload entities and the total count of
    uploads that match the request criteria.
    """
    uploads: List[UploadSelectResponse]
    uploads_count: int
