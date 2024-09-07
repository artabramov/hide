"""
The module defines a FastAPI router for deleting favorite entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.favorite_model import Favorite
from app.schemas.favorite_schemas import (
    FavoriteDeleteRequest, FavoriteDeleteResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.delete("/favorite/{favorite_id}", summary="Delete favorite",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=FavoriteDeleteResponse, tags=["favorites"])
async def favorite_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteDeleteRequest)
) -> FavoriteDeleteResponse:
    """
    FastAPI router for deleting a favorite entity. The router fetches
    the favorite from the repository using the provided ID, verifies
    that the favorite exists and that the current user is the owner of
    the favorite. It updates the favorites count for the associated
    document, executes related hooks, and returns the ID of the deleted
    favorite in a JSON response. The current user should have a reader
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

    await favorite_repository.delete(favorite, commit=False)

    favorite.favorite_document.favorites_count = await favorite_repository.count_all(  # noqa E501
        document_id__eq=favorite.document_id)
    document_repository = Repository(session, cache, Document)
    await document_repository.update(favorite.favorite_document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_FAVORITE_DELETE, favorite)

    await favorite_repository.commit()
    await hook.execute(H.AFTER_FAVORITE_DELETE, favorite)

    return {"favorite_id": favorite.id}
