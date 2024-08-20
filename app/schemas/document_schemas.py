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
    tags: Optional[str] = Field(max_length=256, default=None)
    file: UploadFile = File(...)


class DocumentUploadResponse(BaseModel):
    """Pydantic schema for document uploading response."""
    document_id: int


class DocumentDownloadRequest(BaseModel):
    document_id: int


class DocumentSelectRequest(BaseModel):
    document_id: int


class DocumentSelectResponse(BaseModel):
    id: int
    created_date: int
    updated_date: int
    user_id: int
    collection_id: int

    document_name: str
    document_summary: Optional[str]

    filesize: int
    mimetype: str

    thumbnail_url: Optional[str]
    comments_count: int
    document_tags: list


class DocumentDeleteRequest(BaseModel):
    document_id: int


class DocumentDeleteResponse(BaseModel):
    document_id: int
