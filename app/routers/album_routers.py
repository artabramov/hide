from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.album_models import Album
from app.schemas.album_schemas import (
    AlbumInsertRequest, AlbumInsertResponse,  AlbumSelectRequest,
    AlbumSelectResponse, AlbumUpdateRequest, AlbumUpdateResponse,
    AlbumDeleteRequest, AlbumDeleteResponse, AlbumsListRequest,
    AlbumsListResponse)
from app.repository import Repository
from app.errors import E, Msg
from app.config import get_config
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/album", response_model=AlbumInsertResponse, tags=["albums"])
async def album_insert(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.WRITER)),
                       schema=Depends(AlbumInsertRequest)):

    album_repository = Repository(session, cache, Album)

    album_exists = await album_repository.exists(
        album_name__eq=schema.album_name)

    if album_exists:
        raise E("album_name", schema.album_name, Msg.ALBUM_NAME_EXISTS)

    album = Album(current_user.id, schema.is_locked, schema.album_name,
                  album_summary=schema.album_summary)
    await album_repository.insert(album)

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.AFTER_ALBUM_INSERT, album)

    return {"album_id": album.id}


@router.get("/album/{album_id}", response_model=AlbumSelectResponse, tags=["albums"])  # noqa E501
async def album_select(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.READER)),
                       schema=Depends(AlbumSelectRequest)):

    album_repository = Repository(session, cache, Album)
    album = await album_repository.select(id=schema.album_id)

    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.AFTER_ALBUM_SELECT, album)

    return album.to_dict()


@router.put("/album/{album_id}", response_model=AlbumUpdateResponse, tags=["albums"])  # noqa E501
async def album_update(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.EDITOR)),
                       schema=Depends(AlbumUpdateRequest)):
    album_repository = Repository(session, cache, Album)

    album = await album_repository.select(id=schema.album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    album_exists = await album_repository.exists(
        album_name__eq=schema.album_name, id__ne=album.id)
    if album_exists:
        raise E("album_name", schema.album_name, Msg.ALBUM_NAME_EXISTS)

    album.is_locked = schema.is_locked
    album.album_name = schema.album_name
    album.album_summary = schema.album_summary
    await album_repository.update(album)

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.AFTER_ALBUM_UPDATE, album)

    return {"album_id": album.id}


@router.delete("/album/{album_id}", response_model=AlbumDeleteResponse, tags=["albums"])  # noqa E501
async def album_delete(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.ADMIN)),
                       schema=Depends(AlbumDeleteRequest)):
    album_repository = Repository(session, cache, Album)

    album = await album_repository.select(id=schema.album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # TODO: delete posts with commit=False
    if album.posts_count > 0:
        ...

    await album_repository.delete(album, commit=False)
    await album_repository.commit()

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.AFTER_ALBUM_DELETE, album)

    return {"album_id": album.id}


@router.get("/albums", response_model=AlbumsListResponse, tags=["albums"])
async def albums_list(session=Depends(get_session), cache=Depends(get_cache),
                      current_user: User = Depends(auth(UserRole.READER)),
                      schema=Depends(AlbumsListRequest)):
    album_repository = Repository(session, cache, Album)

    albums = await album_repository.select_all(**schema.__dict__)
    albums_count = await album_repository.count_all(**schema.__dict__)

    return {
        "albums": [album.to_dict() for album in albums],
        "albums_count": albums_count,
    }
