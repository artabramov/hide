from fastapi import APIRouter, Depends, HTTPException, status
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_models import User, UserRole
from app.models.album_models import Album
from app.schemas.album_schemas import (AlbumInsertRequest, AlbumInsertResponse)
from app.repositories.album_repository import AlbumRepository
from app.errors import E, Msg
from app.config import get_config
# from time import time
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/album", response_model=AlbumInsertResponse, tags=["albums"])
async def album_insert(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.WRITER)),
                       schema=Depends(AlbumInsertRequest)):

    album_repository = AlbumRepository(session, cache)
    album_exists = await album_repository.exists(
        album_name__eq=schema.album_name)

    if album_exists:
        raise E("album_name", schema.album_name, Msg.ALBUM_NAME_EXISTS)

    album = Album(current_user.id, schema.is_locked, schema.album_name,
                  album_summary=schema.album_summary)

    hook = Hook(album_repository.entity_manager, album_repository.cache_manager)
    album = await hook.execute(H.BEFORE_ALBUM_INSERT, entity=album)
    album = await album_repository.insert(album)
    album = await hook.execute(H.AFTER_ALBUM_INSERT, entity=album)

    return {"album_id": album.id}


# @router.get("/user/{user_id}", response_model=UserSelectResponse, tags=["users"])  # noqa E501
# async def user_select(session=Depends(get_session), cache=Depends(get_cache),
#                       current_user: User = Depends(auth(UserRole.READER)),
#                       schema=Depends(UserSelectRequest)):
#     """Select user."""
#     user_repository = UserRepository(session, cache)
#     user = await user_repository.select(schema.user_id)

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

#     return {
#         "user": user.to_dict(),
#     }
