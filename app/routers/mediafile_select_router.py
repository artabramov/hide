from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.revision_model import Revision
from app.schemas.mediafile_schemas import MediafileSelectResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_MEDIAFILE_SELECT)

router = APIRouter()


@router.get("/mediafile/{mediafile_id}",
            summary="Retrieve a mediafile data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=MediafileSelectResponse, tags=["mediafiles"])
@locked
async def mediafile_select(
    mediafile_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> MediafileSelectResponse:
    """
    FastAPI router for retrieving a mediafile entity. The router fetches
    the mediafile from the repository using the provided ID, verifies
    that the mediafile exists, executes related hooks, and returns the
    mediafile details in a JSON response. The current user should have
    a reader role or higher. Returns a 200 response on success, a 404
    error if the mediafile is not found, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)

    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)
    mediafile.latest_revision = await revision_repository.select(
        id=mediafile.latest_revision_id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_MEDIAFILE_SELECT, mediafile)

    return mediafile.to_dict()
