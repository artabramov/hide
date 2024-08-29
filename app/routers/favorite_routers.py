"""
This module defines API routes for managing favorites in the
application. It includes endpoints for creating, retrieving, deleting,
and listing favorites. Each endpoint handles specific CRUD operations,
performs necessary validations, updates related document counts, logs
events using hooks, and returns appropriate responses.
"""

from fastapi import APIRouter, Depends, Request, status
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.favorite_models import Favorite
from app.schemas.favorite_schemas import (
    FavoriteInsertRequest, FavoriteInsertResponse, FavoriteSelectRequest,
    FavoriteSelectResponse, FavoriteDeleteRequest, FavoriteDeleteResponse,
    FavoritesListRequest, FavoritesListResponse)
from app.repository import Repository
from app.errors import E
from app.config import get_config
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/favorite", name="Create a favorite",
             tags=["favorites"], response_model=FavoriteInsertResponse)
async def favorite_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteInsertRequest)
) -> dict:
    """
    Allows users with at least a reader role to create a favorite for
    a specific document. It checks for the existence of the document
    and whether the user has already favorited it. If not, it adds the
    favorite and updates the document's favorites count. Returns a 201
    status code upon successful creation. Raises a 404 status code if
    the document is not found and a 403 status code if the user does
    not have the required permissions.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id__eq=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(
        user_id__eq=current_user.id, document_id__eq=schema.document_id)

    if not favorite:
        favorite = Favorite(current_user.id, document.id)
        await favorite_repository.insert(favorite)

    document.favorites_count = await favorite_repository.count_all(
        document_id__eq=document.id)
    await document_repository.update(document)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITE_INSERT, favorite)

    return {"favorite_id": favorite.id}


@router.get("/favorite/{favorite_id}", name="Retrieve a favorite",
            tags=["favorites"], response_model=FavoriteSelectResponse)
async def favorite_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteSelectRequest)
) -> dict:
    """
    Retrieves details of a specific favorite. Ensures the favorite
    exists and that the requesting user has permission to view it.
    Returns a 200 status code with the favorite details. Returns a 404
    status code if the favorite is not found, and a 403 status code if
    the favorite does not belong to the requesting user.
    """
    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(id=schema.favorite_id)

    if not favorite:
        raise E("favorite_id", schema.favorite_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif favorite.user_id != current_user.id:
        raise E("favorite_id", schema.favorite_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITE_SELECT, favorite)

    return favorite.to_dict()


@router.delete("/favorite/{favorite_id}", name="Delete a favorite",
               tags=["favorites"], response_model=FavoriteDeleteResponse)
async def favorite_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteDeleteRequest)
) -> dict:
    """
    Deletes a specific favorite. Validates that the favorite exists and
    that it belongs to the requesting user. Returns a 200 status code
    with the ID of the deleted favorite. Returns a 404 status code if
    the favorite is not found, and a 403 status code if the favorite
    does not belong to the requesting user.
    """
    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(id=schema.favorite_id)

    if not favorite:
        raise E("favorite_id", schema.favorite_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif favorite.user_id != current_user.id:
        raise E("favorite_id", schema.favorite_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    await favorite_repository.delete(favorite)

    favorite.favorite_document.favorites_count = await favorite_repository.count_all(  # noqa E501
        document_id__eq=favorite.document_id)
    document_repository = Repository(session, cache, Document)
    await document_repository.update(favorite.favorite_document)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITE_DELETE, favorite)

    return {"favorite_id": favorite.id}


@router.get("/favorites", name="Retrieve favorites list",
            tags=["favorites"], response_model=FavoritesListResponse)
async def favorites_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoritesListRequest)
) -> dict:
    """
    Retrieves a list of favorites for the current user based on the
    specified query parameters. Returns the list of favorites and their
    count. Raises a 403 status code if the user is not authenticated or
    does not have permission to view the favorites, and a 422 status
    code for invalid query parameters.
    """
    kwargs = schema.__dict__
    kwargs["user_id__eq"] = current_user.id

    favorite_repository = Repository(session, cache, Favorite)
    favorites = await favorite_repository.select_all(**kwargs)
    favorites_count = await favorite_repository.count_all(**kwargs)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITES_LIST, favorites)

    return {
        "favorites": [favorite.to_dict() for favorite in favorites],
        "favorites_count": favorites_count,
    }
