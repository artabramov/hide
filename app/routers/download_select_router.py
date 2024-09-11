"""
The module defines a FastAPI router for retrieving download entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.download_model import Download
from app.schemas.download_schemas import (
    DownloadSelectRequest, DownloadSelectResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/download/{download_id}", summary="Retrieve download",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DownloadSelectResponse, tags=["downloads"])
async def download_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(DownloadSelectRequest)
) -> DownloadSelectResponse:
    """
    FastAPI router for retrieving a download entity. The router fetches
    the download from the repository using the provided ID, executes
    related hooks, and returns the download details in a JSON response.
    The current user should have an admin role. Returns a 200 response
    on success, a 404 error if the download is not found, and a 403
    error if authentication fails or the user does not have the
    required role.
    """
    download_repository = Repository(session, cache, Download)
    download = await download_repository.select(id=schema.download_id)

    if not download:
        raise E("download_id", schema.download_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOWNLOAD_SELECT, download)

    return download.to_dict()
