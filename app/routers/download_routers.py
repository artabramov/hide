"""
This module defines API routes for managing download records. It
includes endpoints to retrieve a single download by its ID and to list
downloads with support for pagination and sorting. The routes use
Pydantic schemas for request and response validation and include hooks
for post-retrieval actions. Access to these endpoints is controlled
based on user roles, and errors are handled with appropriate HTTP status
codes.
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
    Retrieves a download record by its ID, verifies its existence, and
    executes a post-retrieval hook. If the download is not found, a 404
    error is raised. Returns the details of the download as a
    dictionary.
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
    Retrieves a list of download records based on query parameters,
    including pagination and sorting options. Executes a post-retrieval
    hook and returns a dictionary containing the list of downloads and
    the total count. If no downloads are found, returns an empty list.
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
