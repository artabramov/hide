"""
The module defines a FastAPI router for retrieving revision entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.revision_model import Revision
from app.schemas.revision_schemas import (
    RevisionSelectRequest, RevisionSelectResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E

router = APIRouter()


@router.get("/revision/{revision_id}", summary="Retrieve revision",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=RevisionSelectResponse, tags=["revisions"])
async def revision_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(RevisionSelectRequest)
) -> RevisionSelectResponse:
    """
    FastAPI router for retrieving a revision entity. The router fetches
    the revision from the repository using the provided ID, executes
    related hooks, and returns the revision details in a JSON response.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the revision is not found, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=schema.revision_id)

    if not revision:
        raise E("revision_id", schema.revision_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_REVISION_SELECT, revision)

    return revision.to_dict()
