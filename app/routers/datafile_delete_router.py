from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.datafile_model import Datafile
from app.schemas.datafile_schemas import DatafileDeleteResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DATAFILE_DELETE, HOOK_AFTER_DATAFILE_DELETE)

router = APIRouter()


@router.delete("/datafile/{datafile_id}", summary="Delete a datafile",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=DatafileDeleteResponse, tags=["Datafiles"])
@locked
async def datafile_delete(
    datafile_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DatafileDeleteResponse:
    """
    FastAPI router for deleting a datafile entity. The router retrieves
    the datafile from the repository using the provided ID, checks if
    the datafile exists and its collection is not locked, deletes the
    datafile and all related entities, updates the counters for the
    associated collection, executes related hooks, and returns the
    deleted datafile ID in a JSON response. The current user should
    have an admin role. Returns a 200 response on success, a 404 error
    if the datafile is not found, a 423 error if the collection is
    locked, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    datafile_repository = Repository(session, cache, Datafile)
    datafile = await datafile_repository.select(id=datafile_id)

    if not datafile:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif datafile.is_locked:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    await datafile_repository.delete(datafile, commit=False)

    if datafile.collection_id:
        await datafile_repository.lock_all()

        datafile.datafile_collection.datafiles_count = (
            await datafile_repository.count_all(
                collection_id__eq=datafile.collection_id))

        datafile.datafile_collection.revisions_count = (
            await datafile_repository.sum_all(
                "revisions_count", collection_id__eq=datafile.collection_id))

        datafile.datafile_collection.revisions_size = (
            await datafile_repository.sum_all(
                "revisions_size", collection_id__eq=datafile.collection_id))

        collection_repository = Repository(session, cache, Collection)
        await collection_repository.update(
            datafile.datafile_collection, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DATAFILE_DELETE, datafile)

    await datafile_repository.commit()
    await hook.do(HOOK_AFTER_DATAFILE_DELETE, datafile)

    return {"datafile_id": datafile.id}
