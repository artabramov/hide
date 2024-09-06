from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from app.schemas.user_schemas import UserSelectResponse


class RevisionDownloadRequest(BaseModel):
    revision_id: int


class RevisionSelectRequest(BaseModel):
    revision_id: int


class RevisionSelectResponse(BaseModel):
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


class RevisionsListRequest(BaseModel):
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


class RevisionsListResponse(BaseModel):
    revisions: List[RevisionSelectResponse]
    revisions_count: int
