"""
This module defines Pydantic schemas for managing favorites in the
application. It includes schemas for creating, selecting, deleting,
and listing favorites. The schemas cover request and response formats
for various operations, incorporating fields for user IDs, document IDs,
and pagination options, as well as related document details.
"""

from typing import Literal, List
from pydantic import BaseModel, Field
from app.config import get_config
from app.schemas.document_schemas import DocumentSelectResponse

cfg = get_config()


class FavoriteInsertRequest(BaseModel):
    """
    Pydantic schema for creating a new favorite. Requires user ID and
    document ID.
    """
    document_id: int


class FavoriteInsertResponse(BaseModel):
    """
    Pydantic schema for the response after inserting a new favorite.
    Contains the favorite ID.
    """
    favorite_id: int


class FavoriteSelectRequest(BaseModel):
    """
    Pydantic schema for requesting details of a specific favorite
    by its ID.
    """
    favorite_id: int


class FavoriteSelectResponse(BaseModel):
    """
    Pydantic schema for the response when selecting a favorite. Includes
    details about the favorite and the associated document.
    """
    id: int
    created_date: int
    user_id: int
    document_id: int
    favorite_document: DocumentSelectResponse


class FavoriteDeleteRequest(BaseModel):
    """
    Pydantic schema for deleting a favorite by its ID.
    """
    favorite_id: int


class FavoriteDeleteResponse(BaseModel):
    """
    Pydantic schema for the response after deleting a favorite. Contains
    the favorite ID.
    """
    favorite_id: int


class FavoritesListRequest(BaseModel):
    """
    Pydantic schema for listing favorites with pagination and sorting
    options.
    """
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class FavoritesListResponse(BaseModel):
    """
    Pydantic schema for the response containing a list of favorites and
    the total count.
    """
    favorites: List[FavoriteSelectResponse]
    favorites_count: int
