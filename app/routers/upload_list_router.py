"""
The module defines a FastAPI router for retrieving the revision list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.upload_model import Upload
from app.schemas.upload_schemas import (
    UploadListRequest, UploadListResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/uploads", summary="Upload list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UploadListResponse, tags=["uploads"])
@locked
async def upload_list(
    schema=Depends(UploadListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> UploadListResponse:
    """
    FastAPI router for retrieving a list of revision entities. The
    router fetches the list of revisions from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    upload_repository = Repository(session, cache, Upload)

    uploads = await upload_repository.select_all(**schema.__dict__)
    uploads_count = await upload_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.AFTER_UPLOAD_LIST, uploads)

    return {
        "uploads": [upload.to_dict() for upload in uploads],
        "uploads_count": uploads_count,
    }
