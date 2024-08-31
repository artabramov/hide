from typing import Optional
from pydantic import BaseModel


class RevisionSelectResponse(BaseModel):
    id: int
    created_date: int
    updated_date: int
    user_id: int
    document_id: int
    original_filename: str
    encrypted_filename: str
    original_filesize: int
    encrypted_filesize: int
    mimetype: str
    thumbnail_url: Optional[str] = None
    downloads_count: int
