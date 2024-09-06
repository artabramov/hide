"""
The module defines a FastAPI router for deleting comment entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.comment_models import Comment
from app.schemas.comment_schemas import (
    CommentDeleteRequest, CommentDeleteResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.delete("/comment/{comment_id}", summary="Delete comment",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=CommentDeleteResponse, tags=["comments"])
async def comment_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CommentDeleteRequest)
) -> CommentDeleteResponse:
    """
    FastAPI router for deleting a comment entity. The router fetches
    the comment from the repository using the provided ID, verifies
    that the comment exists, ensures the associated collection is not
    locked, and confirms that the current user is the creator of the
    comment. It updates the comment count for the associated document,
    executes related hooks, and returns the ID of the deleted comment
    in a JSON response. The current user should have an editor role or
    higher. Returns a 200 response on success, a 404 error if the
    comment is not found, a 423 error if the collection is locked, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=schema.comment_id)

    if not comment:
        raise E("comment_id", schema.comment_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif comment.comment_document.document_collection.is_locked:
        raise E("comment_id", schema.comment_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    elif comment.user_id != current_user.id:
        raise E("comment_id", schema.comment_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    await comment_repository.delete(comment, commit=False)

    comment.comment_document.comments_count = await comment_repository.count_all(  # noqa E501
        document_id__eq=comment.document_id)
    document_repository = Repository(session, cache, Document)
    await document_repository.update(comment.comment_document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(
        H.BEFORE_COMMENT_DELETE, comment.comment_document.document_collection)

    await comment_repository.commit()
    await hook.execute(
        H.AFTER_COMMENT_DELETE, comment.comment_document.document_collection)

    return {"comment_id": comment.id}
