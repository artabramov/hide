"""
The module defines a FastAPI router for retrieving the option list.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.comment_models import Comment
from app.schemas.comment_schemas import (
    CommentListRequest, CommentListResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/comments", summary="Retrieve comment list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CommentListResponse, tags=["comments"])
async def comment_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CommentListRequest)
) -> CommentListResponse:
    """
    FastAPI router for retrieving a list of comment entities. The router
    fetches the list of comments from the repository, executes related
    hooks, and returns the results in a JSON response. The current user
    should have a reader role or higher. Returns a 200 response on
    success and a 403 error if authentication fails or the user does
    not have the required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comments = await comment_repository.select_all(**schema.__dict__)
    comments_count = await comment_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COMMENT_LIST, comments)

    return {
        "comments": [comment.to_dict() for comment in comments],
        "comments_count": comments_count,
    }
