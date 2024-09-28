"""
The module defines a FastAPI router for retrieving the download list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.download_model import Download
from app.schemas.download_schemas import (
    DownloadListRequest, DownloadListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    HOOK_AFTER_DOWNLOAD_LIST, LOC_PATH, ERR_RESOURCE_NOT_FOUND)
from app.errors import E

router = APIRouter()


@router.get("/mediafile/{mediafile_id}/downloads",
            summary="Retrieve download list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DownloadListResponse, tags=["mediafiles"])
@locked
async def download_list(
    mediafile_id: int, schema=Depends(DownloadListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DownloadListResponse:
    """
    FastAPI router for retrieving a list of download entities. The
    router fetches the list of downloads from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have an admin role. Returns a 200 response on
    success and a 403 error if authentication fails or the user does
    not have the required role.
    """
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)

    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    kwargs = schema.__dict__
    kwargs["mediafile_id__eq"] = mediafile_id

    download_repository = Repository(session, cache, Download)
    downloads = await download_repository.select_all(**kwargs)
    downloads_count = await download_repository.count_all(**kwargs)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DOWNLOAD_LIST, downloads)

    return {
        "downloads": [download.to_dict() for download in downloads],
        "downloads_count": downloads_count,
    }
