"""
The module defines FastAPI routers for managing revisions, including
retrieving details of a specific revision by its ID, downloading the
original file associated with a revision, and listing revisions based
on query parameters.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response, JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.revision_models import Revision
from app.models.download_models import Download
from app.schemas.revision_schemas import (
    RevisionSelectRequest, RevisionSelectResponse, RevisionDownloadRequest,
    RevisionsListRequest, RevisionsListResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.errors import E
from app.config import get_config

cfg = get_config()
router = APIRouter()


@router.get("/revision/{revision_id}", name="Retrieve revision",
            tags=["revisions"], response_model=RevisionSelectResponse)
async def revision_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(RevisionSelectRequest)
) -> dict:
    """
    Retrieve a revision entity by its ID. The router fetches the
    revision from the repository using the provided ID, executes related
    hooks, and returns the result in a JSON response. The current user
    should have a reader role or higher. Returns a 200 response on
    success, a 404 error if the revision is not found, and a 403 error
    if authentication fails or the user does not have the required role.
    """
    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=schema.revision_id)

    if not revision:
        raise E("revision_id", schema.revision_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_REVISION_SELECT, revision)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=revision.to_dict()
    )


@router.get("/revision/{revision_id}/download", tags=["revisions"],
            name="Download revision")
async def revision_download(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(RevisionDownloadRequest)
) -> Response:
    """
    Download a revision file by its ID. The router retrieves the
    specified revision from the repository, decrypts the associated
    file, executes related hooks, and returns the file as an attachment.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the revision is not found, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=schema.revision_id)
    if not revision:
        raise HTTPException(status_code=404)

    data = await FileManager.read(revision.revision_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(current_user.id, revision.revision_document.id,
                        revision.id)
    await download_repository.insert(download, commit=False)

    document_repository = Repository(session, cache, Document)
    revision.revision_document.downloads_count = await download_repository.count_all(  # noqa E501
        document_id__eq=revision.revision_document.id)
    await document_repository.update(revision.revision_document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_REVISION_DOWNLOAD, revision.revision)

    await revision_repository.commit()

    headers = {"Content-Disposition": f"attachment; filename={revision.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=revision.original_mimetype)


@router.get("/revisions", name="Revisions list",
            tags=["revisions"], response_model=RevisionsListResponse)
async def revisions_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(RevisionsListRequest)
) -> dict:
    """
    Retrieve a list of revision entities based on the provided
    parameters. The router fetches the list of revisions from the
    repository, executes related hooks, and returns the results in
    a JSON response. The current user should have a reader role or
    higher. Returns a 200 response on success and a 403 error if
    authentication fails or the user does not have the required role.
    """
    revision_repository = Repository(session, cache, Revision)

    revisions = await revision_repository.select_all(**schema.__dict__)
    revisions_count = await revision_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_REVISIONS_LIST, revisions)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "revisions": [revision.to_dict() for revision in revisions],
            "revisions_count": revisions_count,
        }
    )
