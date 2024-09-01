"""
The module defines FastAPI routers for managing download entities,
including retrieving details of a specific download by its ID and
listing downloads based on query parameters.
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
    Retrieve the details of a specific download entity by its ID. The
    router fetches the download from the repository using the provided
    ID, executes related hooks, and returns a response with the download.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the download is not found, a 403
    error if authentication fails or the user does not have the required
    role.
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
    Retrieve a list of download entities based on the provided query
    parameters. The router fetches the list of downloads from the
    repository, executes related hooks, and returns a response with the
    downloads and the total count of downloads that match the query.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 403 error if authentication fails or the user
    does not have the required role.
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
