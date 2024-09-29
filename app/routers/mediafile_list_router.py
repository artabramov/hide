from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.revision_model import Revision
from app.models.tag_model import Tag
from app.schemas.mediafile_schemas import (
    MediafileListRequest, MediafileListResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.entity_manager import SUBQUERY
from app.constants import HOOK_AFTER_MEDIAFILE_LIST

router = APIRouter()


@router.get("/mediafiles", summary="Retrieve the list of mediafiles.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=MediafileListResponse, tags=["Mediafiles"])
@locked
async def mediafile_list(
    schema=Depends(MediafileListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> MediafileListResponse:
    """
    FastAPI router for retrieving a list of mediafile entities. The
    router fetches the list of mediafiles from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await mediafile_repository.entity_manager.subquery(
            Tag, "mediafile_id", tag_value__eq=schema.tag_value__eq)

    mediafiles = await mediafile_repository.select_all(**kwargs)
    mediafiles_count = await mediafile_repository.count_all(**kwargs)

    revision_repository = Repository(session, cache, Revision)
    for mediafile in mediafiles:
        mediafile.latest_revision = await revision_repository.select(
          id=mediafile.latest_revision_id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_MEDIAFILE_LIST, mediafiles)

    return {
        "mediafiles": [mediafile.to_dict() for mediafile in mediafiles],
        "mediafiles_count": mediafiles_count,
    }
