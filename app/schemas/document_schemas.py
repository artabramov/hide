from typing import Optional
from pydantic import BaseModel, Field
from fastapi import File, UploadFile
from app.config import get_config

cfg = get_config()


class DocumentUploadRequest(BaseModel):
    """Pydantic schema for document uploading request."""
    collection_id: int
    document_name: Optional[str] = Field(min_length=2, max_length=128, default=None)  # noqa E501
    document_summary: Optional[str] = Field(max_length=512, default=None)
    file: UploadFile = File(...)


class DocumentUploadResponse(BaseModel):
    """Pydantic schema for document uploading response."""
    document_id: int


class DocumentDownloadRequest(BaseModel):
    document_id: int
