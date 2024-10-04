from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.datafile_model import Datafile
from app.models.revision_model import Revision
from app.models.tag_model import Tag
from app.schemas.datafile_schemas import (
    DatafileListRequest, DatafileListResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.entity_manager import SUBQUERY
from app.constants import HOOK_AFTER_DATAFILE_LIST

router = APIRouter()


@router.get("/datafiles", summary="Retrieve the list of datafiles.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DatafileListResponse, tags=["Datafiles"])
@locked
async def datafile_list(
    schema=Depends(DatafileListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DatafileListResponse:
    """
    FastAPI router for retrieving a list of datafile entities. The
    router fetches the list of datafiles from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    datafile_repository = Repository(session, cache, Datafile)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await datafile_repository.entity_manager.subquery(
            Tag, "datafile_id", tag_value__eq=schema.tag_value__eq)

    datafiles = await datafile_repository.select_all(**kwargs)
    datafiles_count = await datafile_repository.count_all(**kwargs)

    revision_repository = Repository(session, cache, Revision)
    for datafile in datafiles:
        datafile.latest_revision = await revision_repository.select(
          id=datafile.latest_revision_id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DATAFILE_LIST, datafiles)

    return {
        "datafiles": [datafile.to_dict() for datafile in datafiles],
        "datafiles_count": datafiles_count,
    }
