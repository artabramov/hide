"""
The module defines FastAPI routers for managing comments, including
creating, retrieving, updating, deleting comment entities, and listing
comments pased on query parameters.
"""

from fastapi import APIRouter, Depends, Request, status
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.comment_models import Comment
from app.schemas.comment_schemas import (
    CommentInsertRequest, CommentInsertResponse, CommentSelectRequest,
    CommentSelectResponse, CommentUpdateRequest, CommentUpdateResponse,
    CommentDeleteRequest, CommentDeleteResponse, CommentsListRequest,
    CommentsListResponse)
from app.repository import Repository
from app.errors import E
from app.config import get_config
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/comment", name="Create a comment",
             tags=["comments"], response_model=CommentInsertResponse)
async def comment_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(CommentInsertRequest)
) -> dict:
    """
    Create a new comment entity. The router validates that the document
    exists and that its collection is not locked, inserts the new
    comment into the repository, updates the comment count for the
    associated document, executes related hooks, and returns the created
    comment ID in a JSON response. The current user should have a writer
    role or higher. Returns a 201 response on success, a 404 error if
    the document is not found, a 423 error if the collection is locked,
    and a 403 error if authentication fails or the user does not have
    the required role.
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
    await hook.execute(H.AFTER_COMMENT_INSERT, comment)

    await comment_repository.commit()
    return {"comment_id": comment.id}


@router.get("/comment/{comment_id}", name="Retrieve a comment",
            tags=["comments"], response_model=CommentSelectResponse)
async def comment_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CommentSelectRequest)
) -> dict:
    """
    Retrieve a comment entity by its ID. The router fetches the comment
    from the repository using the provided ID, executes related hooks,
    and returns the result in a JSON response. The current user should
    have a reader role or higher. Returns a 200 response on success,
    a 404 error if the comment is not found, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=schema.comment_id)

    if not comment:
        raise E("comment_id", schema.comment_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COMMENT_SELECT, comment)

    return comment.to_dict()


@router.put("/comment/{comment_id}", name="Update a comment",
            tags=["comments"], response_model=CommentUpdateResponse)
async def comment_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CommentUpdateRequest)
) -> dict:
    """
    Update a comment entity by its ID. The router fetches the comment
    from the repository using the provided ID, verifies that the current
    user is the creator of the comment, checks that the associated
    collection is not locked, updates the comment content, and returns
    the updated comment ID in a JSON response. The current user should
    have an editor role or higher. Returns a 200 response on success,
    a 404 error if the comment is not found, a 423 error if the
    collection is locked, and a 403 error if authentication fails or
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
    await hook.execute(H.AFTER_COMMENT_UPDATE, comment)

    await comment_repository.commit()
    return {"comment_id": comment.id}


@router.delete("/comment/{comment_id}", name="Delete a comment",
               tags=["comments"], response_model=CommentDeleteResponse)
async def comment_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CommentDeleteRequest)
) -> dict:
    """
    Delete a comment entity by its ID. The router fetches the comment
    from the repository using the provided ID, verifies that the comment
    exists, ensures the associated collection is not locked, and
    confirms that the current user is the creator of the comment. It
    updates the comment count for the associated document, executes
    related hooks, and returns the ID of the deleted comment in a JSON
    response. The current user should have an editor role or higher.
    Returns a 200 response on success, a 404 error if the comment is
    not found, a 423 error if the collection is locked, and a 403 error
    if authentication fails or the user does not have the required role.
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
    await hook.execute(H.AFTER_COLLECTION_DELETE,
                       comment.comment_document.document_collection)

    await comment_repository.commit()
    return {"comment_id": comment.id}


@router.get("/comments", name="Retrieve comments list",
            tags=["comments"], response_model=CommentsListResponse)
async def comments_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CommentsListRequest)
) -> dict:
    """
    Retrieve a list of comment entities based on the provided
    parameters. The router fetches the list of comments from the
    repository, executes related hooks, and returns the results in
    a JSON response. The current user should have a reader role or
    higher. Returns a 200 response on success and a 403 error if
    authentication fails or the user does not have the required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comments = await comment_repository.select_all(**schema.__dict__)
    comments_count = await comment_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COMMENTS_LIST, comments)

    return {
        "comments": [comment.to_dict() for comment in comments],
        "comments_count": comments_count,
    }
