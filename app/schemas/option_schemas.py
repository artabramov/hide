from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.config import get_config
from app.schemas.user_schemas import UserSelectResponse
from app.validators.option_validators import (
    validate_option_key, validate_option_value)

cfg = get_config()


class OptionInsertRequest(BaseModel):
    option_key: str = Field(..., min_length=2, max_length=40)
    option_value: Optional[str] = Field(max_length=512, default=None)

    @field_validator("option_key", mode="before")
    def validate_option_key(cls, option_key: str) -> str:
        return validate_option_key(option_key)

    @field_validator("option_value", mode="before")
    def validate_option_value(cls, option_value: str) -> str:
        return validate_option_value(option_value)


class OptionInsertResponse(BaseModel):
    option_id: int


# class CommentSelectRequest(BaseModel):
#     """
#     Pydantic model for the request to select a specific comment
#     by its ID.
#     """
#     comment_id: int


# class CommentSelectResponse(BaseModel):
#     """
#     Pydantic model for the response when retrieving a comment, including
#     its ID, timestamps, user ID, document ID, and content.
#     """
#     id: int
#     created_date: int
#     updated_date: int
#     user_id: int
#     document_id: int
#     comment_content: str
#     comment_user: UserSelectResponse


# class CommentUpdateRequest(BaseModel):
#     """
#     Pydantic model for the request to update an existing comment,
#     including the new comment content. Ensures that the content meets
#     length requirements.
#     """
#     comment_id: int
#     comment_content: str = Field(..., min_length=2, max_length=512)

#     @field_validator("comment_content", mode="before")
#     def validate_comment_content(cls, comment_content: str) -> str:
#         """
#         Pydantic field validator that trims and validates the comment
#         content, ensuring it meets length requirements before further
#         processing.
#         """
#         return validate_comment_content(comment_content)


# class CommentUpdateResponse(BaseModel):
#     """
#     Pydantic model for the response after updating a comment, containing
#     the ID of the updated comment.
#     """
#     comment_id: int


# class CommentDeleteRequest(BaseModel):
#     """
#     Pydantic model for the request to delete a comment by its ID.
#     """
#     comment_id: int


# class CommentDeleteResponse(BaseModel):
#     """
#     Pydantic model for the response after deleting a comment, containing
#     the ID of the deleted comment.
#     """
#     comment_id: int


# class CommentsListRequest(BaseModel):
#     """
#     Pydantic model for the request to list comments, including filtering
#     by document ID, pagination options (offset and limit), and sorting
#     criteria.
#     """
#     document_id__eq: int
#     offset: int = Field(ge=0)
#     limit: int = Field(ge=1, le=200)
#     order_by: Literal["id", "created_date"]
#     order: Literal["asc", "desc"]


# class CommentsListResponse(BaseModel):
#     """
#     Pydantic model for the response when listing comments, containing a
#     list of comments and the total count of comments.
#     """
#     comments: List[CommentSelectResponse]
#     comments_count: int
