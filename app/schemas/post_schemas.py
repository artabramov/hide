from typing import Optional
from pydantic import BaseModel, Field
from fastapi import File, UploadFile
from app.config import get_config

cfg = get_config()


class PostUploadRequest(BaseModel):
    """Pydantic schema for post uploading request."""
    collection_id: int
    post_name: Optional[str] = Field(min_length=2, max_length=128, default=None)  # noqa E501
    post_summary: Optional[str] = Field(max_length=512, default=None)
    file: UploadFile = File(...)


class PostUploadResponse(BaseModel):
    """Pydantic schema for post uploading response."""
    post_id: int
