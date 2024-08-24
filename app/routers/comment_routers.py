"""
This module defines the FastAPI routes for managing comments within the
application. It includes endpoints to create, retrieve, update, delete,
and list comments. Each route handles its respective operation,
validates the request data, checks resource constraints, interacts with
the database, and executes relevant hooks for auditing and
post-processing. It relies on various dependencies such as session
management, caching, user authentication, and schema validation.
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
    Handles the creation of a new comment by validating the associated
    document and collection, inserting the comment into the database,
    updating the document's comment count, and executing any
    post-insertion hooks. Returns the ID of the newly created comment.
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
    Retrieves a comment by its ID, verifies its existence, and executes
    a post-retrieval hook; returns the comment details as a dictionary.
    Raises a 404 error if the comment is not found.
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
    Updates an existing comment if it exists and belongs to the current
    user, checks if the associated collection is unlocked, and executes
    a post-update hook; returns the ID of the updated comment. Raises
    errors if the comment is not found, not owned by the user, or if
    the collection is locked.
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
    Deletes a comment if it exists and the associated collection is not
    locked, updates the comment count for the document, and executes a
    post-deletion hook; returns the ID of the deleted comment. Raises
    errors if the comment is not found or if the collection is locked.
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
    Retrieves a list of comments based on query parameters, including
    pagination and sorting, and executes a post-retrieval hook; returns
    the list of comments along with the total count.
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
