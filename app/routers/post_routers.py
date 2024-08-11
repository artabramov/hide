import uuid
import os
from time import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.album_models import Album
from app.schemas.post_schemas import (
    PostUploadRequest, PostUploadResponse)
from app.errors import E, Msg
from app.hooks import HookAction, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import ImageHelper
from app.config import get_config
from app.models.post_model import Post

router = APIRouter()
cfg = get_config()


@router.post("/post", response_model=PostUploadResponse,
             tags=["posts"], name="Upload post")
async def post_upload(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(PostUploadRequest)
) -> dict:
    """
    Upload a new post to the specified album. Ensures the album exists
    and the user has the writer role or higher before proceeding
    with the upload.
    """
    album_repository = Repository(session, cache, Album)
    album = await album_repository.select(id=schema.album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user_id = current_user.id
    album_id = schema.album_id

    original_filename = schema.file.filename
    post_filename = str(uuid.uuid4())
    post_path = os.path.join(cfg.POST_BASE_PATH, post_filename)
    post_filesize = schema.file.size
    post_mimetype = schema.file.content_type
    post_width = 0
    post_height = 0
    post_duration = 0
    post_bitrate = 0
    post_summary = schema.post_summary

    thumbnail_filename = None

    await FileManager.upload(schema.file, post_path)

    post_repository = Repository(session, cache, Post)
    post = Post(user_id, album_id, original_filename, post_filename,
                post_filesize, post_mimetype, post_width, post_height,
                post_duration, post_bitrate, post_summary, thumbnail_filename)
    await post_repository.insert(post)

    # hook = Hook(session, cache, request, current_user=current_user)
    # await hook.execute(HookAction.after_userpic_upload, current_user)

    return {
        "post_id": post.id
    }
