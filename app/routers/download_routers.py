"""
This module handles operations related to downloads. Users with at least
a reader role can access details about individual downloads and retrieve
lists of downloads. The endpoints cover creating, updating, and deleting
download records, with appropriate validation and access controls. Each
router responds with status codes reflecting success or errors based on
the user's permissions and resource availability.
"""

from fastapi import APIRouter, Depends, Request, status
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.download_models import Download
from app.schemas.download_schemas import (
    DownloadSelectRequest, DownloadSelectResponse, DownloadsListRequest,
    DownloadsListResponse)
from app.repository import Repository
from app.errors import E
from app.config import get_config
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.get("/download/{download_id}", name="Retrieve a download",
            tags=["downloads"], response_model=DownloadSelectResponse)
async def download_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DownloadSelectRequest)
) -> dict:
    """
    Retrieves details of a specific download by its ID. Requires the
    current user to have a reader role or higher. Returns a 200 status
    with the download details if found. Raises a 403 error if the user
    does not have the required permissions or a 404 error if the
    download does not exist.
    """
    download_repository = Repository(session, cache, Download)
    download = await download_repository.select(id=schema.download_id)

    if not download:
        raise E("download_id", schema.download_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOWNLOAD_SELECT, download)

    return download.to_dict()


@router.get("/downloads", name="Retrieve downloads list",
            tags=["downloads"], response_model=DownloadsListResponse)
async def downloads_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DownloadsListRequest)
) -> dict:
    """
    Retrieves a list of downloads and their count based on the provided
    query parameters. Requires the current user to have a reader role or
    higher. Returns a 200 status with the list of downloads and the
    total count. Returns a 403 error if the user does not have the
    required role.
    """
    download_repository = Repository(session, cache, Download)
    downloads = await download_repository.select_all(**schema.__dict__)
    downloads_count = await download_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOWNLOADS_LIST, downloads)

    return {
        "downloads": [download.to_dict() for download in downloads],
        "downloads_count": downloads_count,
    }
