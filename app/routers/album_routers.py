from fastapi import APIRouter, Depends, Request, HTTPException, status
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


@router.post("/album", response_model=AlbumInsertResponse,
             tags=["albums"], name="Create an album")
async def album_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(AlbumInsertRequest)
) -> dict:
    """
    Create a new album if it does not already exist. Requires the user
    to have the writer role or higher. Checks if an album with the same
    name exists, raising an error if it does. Otherwise, creates the
    album with the provided details and returns its ID.
    """
    album_repository = Repository(session, cache, Album)

    album_exists = await album_repository.exists(
        album_name__eq=schema.album_name)

    if album_exists:
        raise E("album_name", schema.album_name, Msg.ALBUM_NAME_EXISTS)

    album = Album(current_user.id, schema.is_locked, schema.album_name,
                  album_summary=schema.album_summary)
    await album_repository.insert(album)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.after_album_insert, album)

    return {"album_id": album.id}


@router.get("/album/{album_id}", response_model=AlbumSelectResponse,
            tags=["albums"], name="Retrieve an album")
async def album_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(AlbumSelectRequest)
) -> dict:
    """
    Retrieve an album by its ID. Returns the album details if found;
    otherwise, raises a 404 error. Requires the user to have the reader
    role or higher.
    """
    album_repository = Repository(session, cache, Album)
    album = await album_repository.select(id=schema.album_id)

    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.after_album_select, album)

    return album.to_dict()


@router.put("/album/{album_id}", response_model=AlbumUpdateResponse,
            tags=["albums"], name="Update an album")
async def album_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(AlbumUpdateRequest)
) -> dict:
    """
    Update an existing album's details by its ID. Requires editor role
    or higher. Raises an error if the album is not found or if the new
    name conflicts with an existing album name. Returns the ID of the
    updated album.
    """
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

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.after_album_update, album)

    return {"album_id": album.id}


@router.delete("/album/{album_id}", response_model=AlbumDeleteResponse,
               tags=["albums"], name="Delete an album")
async def album_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(AlbumDeleteRequest)
) -> dict:
    """
    Delete an album by its ID from the repository. Requires admin role.
    Raises a 404 error if the album is not found. Deletes related posts
    if any exist. Returns the ID of the deleted album.
    """
    album_repository = Repository(session, cache, Album)

    album = await album_repository.select(id=schema.album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if album.posts_count > 0:
        # TODO: delete related posts
        ...

    await album_repository.delete(album, commit=False)
    await album_repository.commit()

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.after_album_delete, album)

    return {"album_id": album.id}


@router.get("/albums", response_model=AlbumsListResponse, tags=["albums"],
            name="Retrieve album list")
async def albums_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(AlbumsListRequest)
) -> dict:
    """
    Retrieve a list of albums based on the provided query parameters.
    Returns the list of albums and the total count. If no albums are
    found, an empty list and zero count are returned. Requires reader
    role or higher.
    """
    album_repository = Repository(session, cache, Album)

    albums = await album_repository.select_all(**schema.__dict__)
    albums_count = await album_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.after_albums_list, albums)

    return {
        "albums": [album.to_dict() for album in albums],
        "albums_count": albums_count,
    }
