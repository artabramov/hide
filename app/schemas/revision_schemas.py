from typing import Optional
from pydantic import BaseModel


class RevisionDownloadRequest(BaseModel):
    revision_id: int


class RevisionSelectResponse(BaseModel):
    id: int
    created_date: int
    user_id: int
    document_id: int
    revision_size: int
    original_filename: str
    original_size: int
    original_mimetype: str
    thumbnail_url: Optional[str] = None
    downloads_count: int
