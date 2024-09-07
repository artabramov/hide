"""
This module defines Pydantic models and validation logic for handling
comment-related operations, including creation, retrieval, updating, and
deletion of comments. It also supports listing comments with pagination
and sorting options. The module includes validation to ensure that
comment content is appropriately formatted.
"""

from typing import Literal, List
from pydantic import BaseModel, Field, field_validator
from app.config import get_config
from app.schemas.user_schemas import UserSelectResponse

cfg = get_config()


def validate_comment_content(comment_content: str) -> str:
    """
    Validates and trims the comment content, ensuring it is at least 2
    characters long after removing leading and trailing whitespace;
    raises a ValueError if the content is too short.
    """
    if len(comment_content.strip()) < 2:
        raise ValueError
    return comment_content.strip()


class CommentInsertRequest(BaseModel):
    """
    Pydantic model for the request to insert a new comment, including
    the document ID and comment content. Ensures that the comment
    content meets length requirements.
    """
    document_id: int
    comment_content: str = Field(..., min_length=2, max_length=512)

    @field_validator("comment_content", mode="before")
    def validate_comment_content(cls, comment_content: str) -> str:
        """
        Pydantic field validator that trims and validates the comment
        content, ensuring it meets length requirements before further
        processing.
        """
        return validate_comment_content(comment_content)


class CommentInsertResponse(BaseModel):
    """
    Pydantic model for the response after inserting a new comment,
    containing the ID of the newly created comment.
    """
    comment_id: int


class CommentSelectRequest(BaseModel):
    """
    Pydantic model for the request to select a specific comment
    by its ID.
    """
    comment_id: int


class CommentSelectResponse(BaseModel):
    """
    Pydantic model for the response when retrieving a comment, including
    its ID, timestamps, user ID, document ID, and content.
    """
    id: int
    created_date: int
    updated_date: int
    user_id: int
    document_id: int
    comment_content: str
    comment_user: UserSelectResponse


class CommentUpdateRequest(BaseModel):
    """
    Pydantic model for the request to update an existing comment,
    including the new comment content. Ensures that the content meets
    length requirements.
    """
    comment_id: int
    comment_content: str = Field(..., min_length=2, max_length=512)

    @field_validator("comment_content", mode="before")
    def validate_comment_content(cls, comment_content: str) -> str:
        """
        Pydantic field validator that trims and validates the comment
        content, ensuring it meets length requirements before further
        processing.
        """
        return validate_comment_content(comment_content)


class CommentUpdateResponse(BaseModel):
    """
    Pydantic model for the response after updating a comment, containing
    the ID of the updated comment.
    """
    comment_id: int


class CommentDeleteRequest(BaseModel):
    """
    Pydantic model for the request to delete a comment by its ID.
    """
    comment_id: int


class CommentDeleteResponse(BaseModel):
    """
    Pydantic model for the response after deleting a comment, containing
    the ID of the deleted comment.
    """
    comment_id: int


class CommentListRequest(BaseModel):
    """
    Pydantic model for the request to list comments, including filtering
    by document ID, pagination options (offset and limit), and sorting
    criteria.
    """
    document_id__eq: int
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date"]
    order: Literal["asc", "desc"]


class CommentListResponse(BaseModel):
    """
    Pydantic model for the response when listing comments, containing a
    list of comments and the total count of comments.
    """
    comments: List[CommentSelectResponse]
    comments_count: int
