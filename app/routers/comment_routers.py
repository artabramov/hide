"""
This module manages comments with endpoints to create, retrieve, update,
and delete them. It requires specific user roles for different actions:
creating or updating comments needs a writer or higher role, and
deleting comments requires an admin role. Responses include status codes
for success or various errors such as forbidden actions, missing
resources, or invalid attributes.
"""

from fastapi import APIRouter, Depends, Request, status
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
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
    Creates a new comment for a specified document. Validates the
    existence and status of the document and its collection. Inserts
    the comment into the database, updates the document's comment count,
    and returns the ID of the created comment. The user must have a
    writer role or higher. Returns a 201 Created status on success.
    Raises a 404 error if the document is not found, a 403 error if
    the collection is locked or does not exist, and a 422 error for
    issues with comment validation.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id__eq=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(
        id__eq=document.collection_id)

    if not collection or collection.is_locked:
        raise E("document_id", schema.document_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    comment_repository = Repository(session, cache, Comment)
    comment = Comment(current_user.id, document.id, schema.comment_content)
    await comment_repository.insert(comment)

    document.comments_count = await comment_repository.count_all(
        document_id__eq=document.id)
    await document_repository.update(document)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COMMENT_INSERT, comment)

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
    Retrieves a specific comment by its ID. Validates that the comment
    exists and returns its details. The user must have a reader role or
    higher to access the comment. Returns a 200 OK status with the
    comment details. Raises a 404 error if the comment is not found.
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
    Updates an existing comment for a specified document. Validates the
    existence of the comment, checks that the current user is the author
    of the comment, and ensures the associated collection is not locked.
    Requires the user to have an editor role or higher. Returns a 200
    status on success. Raises a 404 error if the comment is not found,
    a 403 error if the current user does not own the comment, and a 423
    error if the collection is locked.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=schema.comment_id)

    if not comment:
        raise E("comment_id", schema.comment_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif comment.user_id != current_user.id:
        raise E("comment_id", schema.comment_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(
        id=comment.comment_document.collection_id)

    if not collection or collection.is_locked:
        raise E("comment_id", schema.comment_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    comment.comment_content = schema.comment_content
    await comment_repository.update(comment)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COMMENT_UPDATE, comment)

    return {"comment_id": comment.id}


@router.delete("/comment/{comment_id}", name="Delete a comment",
               tags=["comments"], response_model=CommentDeleteResponse)
async def comment_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(CommentDeleteRequest)
) -> dict:
    """
    Deletes a specified comment. Validates the existence of the comment
    and checks that the associated collection is not locked. Requires
    the user to have an admin role. Returns a 200 status on success.
    Raises a 404 error if the comment is not found, and a 423 error if
    the collection is locked or does not exist.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=schema.comment_id)

    if not comment:
        raise E("comment_id", schema.comment_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(
        id=comment.comment_document.collection_id)

    if not collection or collection.is_locked:
        raise E("comment_id", schema.comment_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    await comment_repository.delete(comment, commit=False)
    await comment_repository.commit()

    comment.comment_document.comments_count = await comment_repository.count_all(  # noqa E501
        document_id__eq=comment.document_id)
    document_repository = Repository(session, cache, Document)
    await document_repository.update(comment.comment_document)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_DELETE, collection)

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
    Retrieves a list of comments based on the provided query parameters.
    Requires the user to have a reader role or higher. Returns a 200
    response on success. Raises a 403 error if the user does not have
    the required role or if the token is missing.
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
