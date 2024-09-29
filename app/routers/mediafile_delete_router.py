from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.mediafile_model import Mediafile
from app.schemas.mediafile_schemas import MediafileDeleteResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_MEDIAFILE_DELETE, HOOK_AFTER_MEDIAFILE_DELETE)

router = APIRouter()


@router.delete("/mediafile/{mediafile_id}", summary="Delete a mediafile",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=MediafileDeleteResponse, tags=["Mediafiles"])
@locked
async def mediafile_delete(
    mediafile_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> MediafileDeleteResponse:
    """
    FastAPI router for deleting a mediafile entity. The router retrieves
    the mediafile from the repository using the provided ID, checks if
    the mediafile exists and its collection is not locked, deletes the
    mediafile and all related entities, updates the counters for the
    associated collection, executes related hooks, and returns the
    deleted mediafile ID in a JSON response. The current user should
    have an admin role. Returns a 200 response on success, a 404 error
    if the mediafile is not found, a 423 error if the collection is
    locked, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)

    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif mediafile.is_locked:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    await mediafile_repository.delete(mediafile, commit=False)

    if mediafile.collection_id:
        await mediafile_repository.lock_all()

        mediafile.mediafile_collection.mediafiles_count = (
            await mediafile_repository.count_all(
                collection_id__eq=mediafile.collection_id))

        mediafile.mediafile_collection.revisions_count = (
            await mediafile_repository.sum_all(
                "revisions_count", collection_id__eq=mediafile.collection_id))

        mediafile.mediafile_collection.revisions_size = (
            await mediafile_repository.sum_all(
                "revisions_size", collection_id__eq=mediafile.collection_id))

        collection_repository = Repository(session, cache, Collection)
        await collection_repository.update(
            mediafile.mediafile_collection, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_MEDIAFILE_DELETE, mediafile)

    await mediafile_repository.commit()
    await hook.do(HOOK_AFTER_MEDIAFILE_DELETE, mediafile)

    return {"mediafile_id": mediafile.id}
