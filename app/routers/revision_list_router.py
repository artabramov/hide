"""
The module defines a FastAPI router for retrieving the revision list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.revision_model import Revision
from app.schemas.revision_schemas import (
    RevisionListRequest, RevisionListResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import HOOK_AFTER_REVISION_LIST

router = APIRouter()


@router.get("/revisions", summary="Revision list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=RevisionListResponse, tags=["revisions"])
@locked
async def revision_list(
    schema=Depends(RevisionListRequest),
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
    revision_repository = Repository(session, cache, Revision)

    revisions = await revision_repository.select_all(**schema.__dict__)
    revisions_count = await revision_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_REVISION_LIST, revisions)

    return {
        "revisions": [revision.to_dict() for revision in revisions],
        "revisions_count": revisions_count,
    }