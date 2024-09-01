"""
The module defines FastAPI routers for managing favorites, including
creating, retrieving, deleting, and listing favorite entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
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
    Create a new favorite entity. The router checks if the specified
    document exists, creates a favorite record if it does not already
    exist for the current user and document, updates the favorites
    count for the document, and executes related hooks. Returns the ID
    of the created favorite in a JSON response. The current user should
    have a reader role or higher. Returns a 201 response on success,
    a 404 error if the document is not found, and a 403 error if
    authentication fails or the user does not have the required role.
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
        await favorite_repository.insert(favorite, commit=False)

    document.favorites_count = await favorite_repository.count_all(
        document_id__eq=document.id)
    await document_repository.update(document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITE_INSERT, favorite)

    await favorite_repository.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"favorite_id": favorite.id}
    )


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
    Retrieve a favorite entity by its ID. The router fetches the
    favorite from the repository using the provided ID, verifies that
    the favorite exists, and checks that the current user is the owner
    of the favorite. It executes related hooks and returns the favorite
    details in a JSON response. The current user should have a reader
    role or higher. Returns a 200 response on success, a 404 error if
    the favorite is not found, and a 403 error if authentication fails
    or the user does not have the required role.
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=favorite.to_dict()
    )


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
    Delete a favorite entity by its ID. The router fetches the favorite
    from the repository using the provided ID, verifies that the favorite
    exists and that the current user is the owner of the favorite. It
    updates the favorites count for the associated document, executes
    related hooks, and returns the ID of the deleted favorite in a JSON
    response. The current user should have a reader role or higher.
    Returns a 200 response on success, a 404 error if the favorite is
    not found, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(id=schema.favorite_id)

    if not favorite:
        raise E("favorite_id", schema.favorite_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif favorite.user_id != current_user.id:
        raise E("favorite_id", schema.favorite_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    await favorite_repository.delete(favorite, commit=False)

    favorite.favorite_document.favorites_count = await favorite_repository.count_all(  # noqa E501
        document_id__eq=favorite.document_id)
    document_repository = Repository(session, cache, Document)
    await document_repository.update(favorite.favorite_document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITE_DELETE, favorite)

    await favorite_repository.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"favorite_id": favorite.id}
    )


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
    Retrieve a list of favorite entities based on the provided
    parameters. The router fetches the list of favorites from the
    repository for the current user, executes related hooks, and
    returns the results in a JSON response. The current user should
    have a reader role or higher. Returns a 200 response on success
    and a 403 error if authentication fails or the user does not have
    the required role.
    """
    kwargs = schema.__dict__
    kwargs["user_id__eq"] = current_user.id

    favorite_repository = Repository(session, cache, Favorite)
    favorites = await favorite_repository.select_all(**kwargs)
    favorites_count = await favorite_repository.count_all(**kwargs)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITES_LIST, favorites)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "favorites": [favorite.to_dict() for favorite in favorites],
            "favorites_count": favorites_count,
        }
    )
