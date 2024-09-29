"""
The module defines a FastAPI router for creating comment entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.comment_model import Comment
from app.schemas.comment_schemas import (
    CommentInsertRequest, CommentInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_COMMENT_INSERT, HOOK_AFTER_COMMENT_INSERT)

router = APIRouter()


@router.post("/comment", summary="Create a new comment",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CommentInsertResponse, tags=["Comments"])
@locked
async def comment_insert(
    schema: CommentInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> CommentInsertResponse:
    """
    FastAPI router for creating a comment entity. The router validates
    that the mediafile exists and that its collection is not locked,
    inserts the new comment into the repository, updates the comment
    count for the associated mediafile, executes related hooks, and
    returns the created comment ID in a JSON response. The current user
    should have a writer role or higher. Returns a 201 response on
    success, a 404 error if the mediafile is not found, a 423 error if
    the collection is locked, and a 403 error if authentication fails
    or the user does not have the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id__eq=schema.mediafile_id)

    if not mediafile:
        raise E([LOC_BODY, "mediafile_id"], schema.mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif mediafile.is_locked:
        raise E([LOC_BODY, "mediafile_id"], schema.mediafile_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    comment_repository = Repository(session, cache, Comment)
    comment = Comment(current_user.id, mediafile.id, schema.comment_content)
    await comment_repository.insert(comment, commit=False)

    await comment_repository.lock_all()
    mediafile.comments_count = await comment_repository.count_all(
        mediafile_id__eq=mediafile.id)
    await mediafile_repository.update(mediafile, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COMMENT_INSERT, comment)

    await comment_repository.commit()
    await hook.do(HOOK_AFTER_COMMENT_INSERT, comment)

    return {"comment_id": comment.id}
