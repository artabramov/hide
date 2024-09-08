"""
The module defines Pydantic schemas for managing documents. Includes
schemas for inserting, selecting, updating, deleting, and listing
documents.
"""

from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.revision_schemas import RevisionSelectResponse
from app.validators.document_validators import (
    validate_document_name, validate_document_summary)


class DocumentInsertRequest(BaseModel):
    """
    Pydantic schema for request to create a new document entity.
    Requires the collection ID to be specified, and optionally the
    document name, document summary, and tags.
    """
    collection_id: int
    document_name: Optional[str] = Field(max_length=256, default=None)
    document_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)

    @field_validator("document_name", mode="before")
    def validate_document_name(cls, document_name: str = None) -> Union[str, None]:  # noqa E501
        return validate_document_name(document_name)

    @field_validator("document_summary", mode="before")
    def validate_document_summary(cls, document_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_document_summary(document_summary)


class DocumentInsertResponse(BaseModel):
    """
    Pydantic schema for the response after creating a new document
    entity. Includes the ID assigned to the newly created document.
    """
    document_id: int


class DocumentSelectRequest(BaseModel):
    """
    Pydantic schema for request to retrieve a document entity. Requires
    the document ID to be specified.
    """
    document_id: int


class DocumentSelectResponse(BaseModel):
    """
    Pydantic schema for the response after retrieving a document entity.
    Includes the document ID, creation and update dates, user ID,
    collection ID, document name, summary, size, and various counts
    such as revisions, comments, downloads, and favorites. Also includes
    the document tags and the latest revision details.
    """
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
    latest_revision: RevisionSelectResponse


class DocumentUpdateRequest(BaseModel):
    """
    Pydantic schema for request to update an existing document entity.
    Requires the document ID and collection ID to be specified, and
    optionally the document name, summary, and tags.
    """
    document_id: int
    collection_id: int
    document_name: str = Field(..., min_length=1, max_length=256)
    document_summary: Optional[str] = Field(max_length=512, default=None)
    tags: Optional[str] = Field(max_length=256, default=None)

    @field_validator("document_name", mode="before")
    def validate_document_name(cls, document_name: str = None) -> str:
        return validate_document_name(document_name)

    @field_validator("document_summary", mode="before")
    def validate_document_summary(cls, document_summary: str = None) -> Union[str, None]:  # noqa E501
        return validate_document_summary(document_summary)


class DocumentUpdateResponse(BaseModel):
    """
    Pydantic schema for the response after updating a document entity.
    Includes the ID assigned to the updated document.
    """
    document_id: int


class DocumentDeleteRequest(BaseModel):
    """
    Pydantic schema for request to delete a document entity. Requires
    the document ID to be specified.
    """
    document_id: int


class DocumentDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after updating a document entity.
    Includes the ID assigned to the deleted document.
    """
    document_id: int


class DocumentListRequest(BaseModel):
    """
    Pydantic schema for requesting a list of document entities. Requires
    pagination options with offset and limit, ordering criteria, and
    optional filters for document name and tag value.
    """
    document_name__ilike: Optional[str] = None
    tag_value__eq: Optional[str] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_id",
                      "collection_id", "document_name", "filesize",
                      "mimetype", "comments_count"]
    order: Literal["asc", "desc"]


class DocumentListResponse(BaseModel):
    """
    Pydantic schema for the response when listing document entities.
    Includes a list of document entities and the total count of
    documents that match the request criteria.
    """
    documents: List[DocumentSelectResponse]
    documents_count: int
