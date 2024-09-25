"""
The module defines a FastAPI router for retrieving the download list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.download_model import Download
from app.schemas.download_schemas import (
    DownloadListRequest, DownloadListResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/downloads", summary="Retrieve download list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DownloadListResponse, tags=["downloads"])
@locked
async def download_list(
    schema=Depends(DownloadListRequest),
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
    download_repository = Repository(session, cache, Download)
    downloads = await download_repository.select_all(**schema.__dict__)
    downloads_count = await download_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(H.AFTER_DOWNLOAD_LIST, downloads)

    return {
        "downloads": [download.to_dict() for download in downloads],
        "downloads_count": downloads_count,
    }
