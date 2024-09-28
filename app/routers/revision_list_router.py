"""
The module defines a FastAPI router for retrieving the revision list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.revision_model import Revision
from app.schemas.revision_schemas import (
    RevisionListRequest, RevisionListResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import (
    LOC_PATH, HOOK_AFTER_REVISION_LIST, ERR_RESOURCE_NOT_FOUND)
from app.errors import E

router = APIRouter()


@router.get("/mediafile/{mediafile_id}/revisions",
            summary="Retrieve the revisions list for a specified mediafile.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=RevisionListResponse, tags=["mediafiles"])
@locked
async def revision_list(
    mediafile_id: int, schema=Depends(RevisionListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> RevisionListResponse:
    """
    FastAPI router for retrieving a list of revision entities. The
    router fetches the list of revisions from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)

    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)

    kwargs = schema.__dict__
    kwargs["mediafile_id__eq"] = mediafile_id

    revisions = await revision_repository.select_all(**kwargs)
    revisions_count = await revision_repository.count_all(**kwargs)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_REVISION_LIST, revisions)

    return {
        "revisions": [revision.to_dict() for revision in revisions],
        "revisions_count": revisions_count,
    }
