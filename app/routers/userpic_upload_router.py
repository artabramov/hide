import uuid
import os
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import (
    UserpicUploadRequest, UserpicUploadResponse)
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import image_resize
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.post("/user/{user_id}/userpic", summary="Upload userpic",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=UserpicUploadResponse, tags=["users"])
async def userpic_upload(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserpicUploadRequest)
) -> UserpicUploadResponse:
    """
    FastAPI router for uploading a userpic. Deletes the existing
    userpic if it exists, uploads and saves a new one, resizes it to
    the specified dimensions, and updates the user's data with the new
    userpic. Allowed for the current user only. Requires the user to
    have a reader role or higher. Returns a 200 response with the
    user ID. Raises a 403 error if the user attempts to upload a
    userpic for a different user, or if the user's token is invalid.
    Raises a 422 error if the file's MIME type is unsupported.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    elif schema.file.content_type not in cfg.USERPIC_MIMES:
        raise E("user_id", schema.user_id, E.MIMETYPE_UNSUPPORTED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if current_user.userpic_filename:
        await FileManager.delete(current_user.userpic_path)

    userpic_filename = str(uuid.uuid4()) + cfg.USERPIC_EXTENSION
    userpic_path = os.path.join(cfg.USERPIC_BASE_PATH, userpic_filename)
    await FileManager.upload(schema.file, userpic_path)

    await image_resize(userpic_path, cfg.USERPIC_WIDTH,
                       cfg.USERPIC_HEIGHT, cfg.USERPIC_QUALITY)

    user_repository = Repository(session, cache, User)
    current_user.userpic_filename = userpic_filename
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_USERPIC_UPLOAD, current_user)

    await user_repository.commit()
    await hook.execute(H.AFTER_USERPIC_UPLOAD, current_user)

    return {"user_id": current_user.id}
