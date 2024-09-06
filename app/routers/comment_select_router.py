"""
The module defines a FastAPI router for retrieving comment entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.comment_models import Comment
from app.schemas.comment_schemas import (
    CommentSelectRequest, CommentSelectResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/comment/{comment_id}", summary="Retrieve comment",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CommentSelectResponse, tags=["comments"])
async def comment_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CommentSelectRequest)
) -> CommentSelectResponse:
    """
    FastAPI router for retrieving a comment entity. The router fetches
    the comment from the repository using the provided ID, executes
    related hooks, and returns the comment details in a JSON response.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the comment is not found, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=schema.comment_id)

    if not comment:
        raise E("comment_id", schema.comment_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COMMENT_SELECT, comment)

    return comment.to_dict()
