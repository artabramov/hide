from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.datafile_model import Datafile
from app.models.revision_model import Revision
from app.schemas.datafile_schemas import DatafileSelectResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_DATAFILE_SELECT)

router = APIRouter()


@router.get("/datafile/{datafile_id}",
            summary="Retrieve a datafile data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DatafileSelectResponse, tags=["Datafiles"])
@locked
async def datafile_select(
    datafile_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DatafileSelectResponse:
    """
    FastAPI router for retrieving a datafile entity. The router fetches
    the datafile from the repository using the provided ID, verifies
    that the datafile exists, executes related hooks, and returns the
    datafile details in a JSON response. The current user should have
    a reader role or higher. Returns a 200 response on success, a 404
    error if the datafile is not found, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    datafile_repository = Repository(session, cache, Datafile)
    datafile = await datafile_repository.select(id=datafile_id)

    if not datafile:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)
    datafile.latest_revision = await revision_repository.select(
        id=datafile.latest_revision_id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DATAFILE_SELECT, datafile)

    return datafile.to_dict()
