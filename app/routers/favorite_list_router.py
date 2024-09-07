"""
The module defines a FastAPI router for retrieving the favorite list.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.favorite_models import Favorite
from app.schemas.favorite_schemas import (
    FavoriteListRequest, FavoriteListResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/favorites", summary="Retrieve favorite list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=FavoriteListResponse, tags=["favorites"])
async def favorite_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteListRequest)
) -> FavoriteListResponse:
    """
    FastAPI router for retrieving a list of favorite entities. The
    router fetches the list of favorites from the repository for the
    current user, executes related hooks, and returns the results in
    a JSON response. The current user should have a reader role or
    higher. Returns a 200 response on success and a 403 error if
    authentication fails or the user does not have the required role.
    """
    kwargs = schema.__dict__
    kwargs["user_id__eq"] = current_user.id

    favorite_repository = Repository(session, cache, Favorite)
    favorites = await favorite_repository.select_all(**kwargs)
    favorites_count = await favorite_repository.count_all(**kwargs)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_FAVORITE_LIST, favorites)

    return {
        "favorites": [favorite.to_dict() for favorite in favorites],
        "favorites_count": favorites_count,
    }
