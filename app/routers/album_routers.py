from fastapi import APIRouter, Depends, HTTPException, status
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_models import User, UserRole
from app.models.album_models import Album
from app.schemas.album_schemas import (AlbumInsertRequest, AlbumInsertResponse,
                                       AlbumSelectRequest, AlbumSelectResponse,
                                       AlbumUpdateRequest, AlbumUpdateResponse)
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
    await album_repository.insert(album)

    hook = Hook(session, cache)
    await hook.execute(H.AFTER_ALBUM_INSERT, album)

    return {"album_id": album.id}


@router.get("/album/{album_id}", response_model=AlbumSelectResponse, tags=["albums"])  # noqa E501
async def album_select(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.READER)),
                       schema=Depends(AlbumSelectRequest)):
    """Select album."""
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id=schema.album_id)

    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache)
    await hook.execute(H.AFTER_ALBUM_SELECT, album)

    return album.to_dict()


@router.put("/album/{album_id}", response_model=AlbumUpdateResponse, tags=["albums"])  # noqa E501
async def update_album(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.EDITOR)),
                       schema=Depends(AlbumUpdateRequest)):
    album_repository = AlbumRepository(session, cache)
    album = await album_repository.select(album_id=schema.album_id)

    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    album.is_locked = schema.is_locked
    album.album_name = schema.album_name
    album.album_summary = schema.album_summary
    await album_repository.update(album)

    hook = Hook(session, cache)
    await hook.execute(H.AFTER_ALBUM_UPDATE, album)

    return {"album_id": album.id}
