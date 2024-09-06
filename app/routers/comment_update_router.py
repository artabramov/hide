"""
The module defines a FastAPI router for updating comment entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.comment_models import Comment
from app.schemas.comment_schemas import (
    CommentUpdateRequest, CommentUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.put("/comment/{comment_id}", name="Update comment",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CommentUpdateResponse, tags=["comments"])
async def comment_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CommentUpdateRequest)
) -> CommentUpdateResponse:
    """
    FastAPI router for updating a comment entity. The router fetches
    the comment from the repository using the provided ID, verifies
    that the current user is the creator of the comment, checks that
    the associated collection is not locked, updates the comment content,
    and returns the updated comment ID in a JSON response. The current
    user should have an editor role or higher. Returns a 200 response
    on success, a 404 error if the comment is not found, a 423 error if
    the collection is locked, and a 403 error if authentication fails or
    the user does not have the required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=schema.comment_id)

    if not comment:
        raise E("comment_id", schema.comment_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif comment.user_id != current_user.id:
        raise E("comment_id", schema.comment_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    elif comment.comment_document.document_collection.is_locked:
        raise E("comment_id", schema.comment_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    comment.comment_content = schema.comment_content
    await comment_repository.update(comment, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_COMMENT_UPDATE, comment)

    await comment_repository.commit()
    await hook.execute(H.AFTER_COMMENT_UPDATE, comment)

    return {"comment_id": comment.id}
