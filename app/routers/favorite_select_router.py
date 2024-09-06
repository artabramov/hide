"""
The module defines a FastAPI router for retrieving favorite entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.favorite_models import Favorite
from app.schemas.favorite_schemas import (
    FavoriteSelectRequest, FavoriteSelectResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/favorite/{favorite_id}", name="Retrieve favorite",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=FavoriteSelectResponse, tags=["favorites"])
async def favorite_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteSelectRequest)
) -> FavoriteSelectResponse:
    """
    FastAPI router for retrieving a favorite entity. The router fetches
    the favorite from the repository using the provided ID, verifies
    that the favorite exists, and checks that the current user is the
    owner of the favorite. It executes related hooks and returns the
    favorite details in a JSON response. The current user should have
    a reader role or higher. Returns a 200 response on success, a 404
    error if the favorite is not found, and a 403 error if
    authentication fails or the user does not have the required role.
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
