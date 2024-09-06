"""
The module defines a FastAPI router for creating comment entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.comment_models import Comment
from app.schemas.comment_schemas import (
    CommentInsertRequest, CommentInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.post("/comment", name="Create comment",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CommentInsertResponse, tags=["comments"])
async def comment_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(CommentInsertRequest)
) -> CommentInsertResponse:
    """
    FastAPI router for creating a comment entity. The router validates
    that the document exists and that its collection is not locked,
    inserts the new comment into the repository, updates the comment
    count for the associated document, executes related hooks, and
    returns the created comment ID in a JSON response. The current user
    should have a writer role or higher. Returns a 201 response on
    success, a 404 error if the document is not found, a 423 error if
    the collection is locked, and a 403 error if authentication fails
    or the user does not have the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id__eq=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise E("document_id", schema.document_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    comment_repository = Repository(session, cache, Comment)
    comment = Comment(current_user.id, document.id, schema.comment_content)
    await comment_repository.insert(comment, commit=False)

    document.comments_count = await comment_repository.count_all(
        document_id__eq=document.id)
    await document_repository.update(document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_COMMENT_INSERT, comment)

    await comment_repository.commit()
    await hook.execute(H.AFTER_COMMENT_INSERT, comment)

    return {"comment_id": comment.id}
