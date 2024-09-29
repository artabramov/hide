"""
The module defines a FastAPI router for creating favorite entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.favorite_model import Favorite
from app.schemas.favorite_schemas import (
    FavoriteInsertRequest, FavoriteInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_FAVORITE_INSERT,
    HOOK_AFTER_FAVORITE_INSERT)

router = APIRouter()


@router.post("/favorite", summary="Create favorite",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=FavoriteInsertResponse, tags=["Favorites"])
@locked
async def favorite_insert(
    schema: FavoriteInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FavoriteInsertResponse:
    """
    FastAPI router for creating a comment entity. The router verifies
    if the specified mediafile exists, creates a favorite record if it
    does not already exist for the current user and mediafile, updates
    the favorites count for the mediafile, and executes related hooks.
    Returns the ID of the created favorite in a JSON response. The
    current user should have a reader role or higher. Returns a 201
    response on success, a 404 error if the mediafile is not found,
    and a 403 error if authentication fails or the user does not have
    the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id__eq=schema.mediafile_id)

    if not mediafile:
        raise E([LOC_BODY, "mediafile_id"], schema.mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(
        user_id__eq=current_user.id, mediafile_id__eq=schema.mediafile_id)

    if not favorite:
        favorite = Favorite(current_user.id, mediafile.id)
        await favorite_repository.insert(favorite, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_FAVORITE_INSERT, favorite)

    await favorite_repository.commit()
    await hook.do(HOOK_AFTER_FAVORITE_INSERT, favorite)

    return {"favorite_id": favorite.id}
