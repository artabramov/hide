from typing import Optional, Literal, List
from pydantic import BaseModel, Field
# from app.schemas.revision_schemas import RevisionSelectResponse
from app.config import get_config

DOCUMENT_NAME_LENGTH = 128

cfg = get_config()


class DocumentInsertRequest(BaseModel):
    """Pydantic schema for document uploading request."""
    collection_id: int
    document_name: Optional[str] = Field(max_length=DOCUMENT_NAME_LENGTH,
                                         default=None)
    document_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)


class DocumentInsertResponse(BaseModel):
    """Pydantic schema for document uploading response."""
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
    document_summary: Optional[str] = None
    document_size: int

    revisions_count: int
    revisions_size: int

    comments_count: int
    downloads_count: int
    favorites_count: int
    document_tags: list


class DocumentUpdateRequest(BaseModel):
    document_id: int
    collection_id: int
    document_name: Optional[str] = Field(min_length=2, max_length=256)
    document_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)


class DocumentUpdateResponse(BaseModel):
    document_id: int


class DocumentDeleteRequest(BaseModel):
    document_id: int


class DocumentDeleteResponse(BaseModel):
    document_id: int


class DocumentsListRequest(BaseModel):
    document_name__ilike: Optional[str] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_id", "document_name", "filesize",
                      "mimetype", "comments_count"]
    order: Literal["asc", "desc"]


class DocumentsListResponse(BaseModel):
    documents: List[DocumentSelectResponse]
    documents_count: int
