import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.mediafile_model import Mediafile
from app.models.revision_model import Revision
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.mediafile_schemas import MediafileReplaceResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import thumbnail_create
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_MEDIAFILE_REPLACE, HOOK_AFTER_MEDIAFILE_REPLACE)

cfg = get_config()
router = APIRouter()


@router.post("/mediafile/{mediafile_id}", summary="Replace a mediafile",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=MediafileReplaceResponse, tags=["mediafiles"])
@locked
async def mediafile_replace(
    mediafile_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> MediafileReplaceResponse:

    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)

    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif mediafile.is_locked:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    # upload file
    revision_filename = str(uuid.uuid4()) + cfg.REVISIONS_EXTENSION
    revision_path = os.path.join(cfg.REVISIONS_BASE_PATH, revision_filename)
    await FileManager.upload(file, revision_path)

    # create thumbnail
    thumbnail_filename = None
    try:
        mimetype = file.content_type
        thumbnail_filename = await thumbnail_create(revision_path, mimetype)
    except Exception:
        pass

    try:
        # encrypt file
        data = await FileManager.read(revision_path)
        encrypted_data = await FileManager.encrypt(data)
        await FileManager.write(revision_path, encrypted_data)

        # insert revision
        revision_repository = Repository(session, cache, Revision)
        revision = Revision(
            current_user.id, mediafile.id, revision_filename,
            os.path.getsize(revision_path), file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # update previous revision
        revision_repository = Repository(session, cache, Revision)
        mediafile.latest_revision.is_latest = False
        await revision_repository.update(
            mediafile.latest_revision, commit=False)

        # update mediafile counters and name
        await revision_repository.lock_all()
        mediafile.revisions_count = await revision_repository.count_all(
            mediafile_id__eq=mediafile.id)
        mediafile.revisions_size = await revision_repository.sum_all(
            "revision_size", mediafile_id__eq=mediafile.id)
        mediafile.mediafile_name = file.filename
        await mediafile_repository.update(mediafile, commit=False)

        # update collection counters
        if mediafile.collection_id:
            await mediafile_repository.lock_all()

            mediafile.mediafile_collection.revisions_count = (
                await mediafile_repository.sum_all(
                    "revisions_count",
                    collection_id__eq=mediafile.collection_id))

            mediafile.mediafile_collection.revisions_size = (
                await mediafile_repository.sum_all(
                    "revisions_size",
                    collection_id__eq=mediafile.collection_id))

            collection_repository = Repository(session, cache, Collection)
            await collection_repository.update(
                mediafile.mediafile_collection, commit=False)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_MEDIAFILE_REPLACE, mediafile)

        await mediafile_repository.commit()
        await hook.do(HOOK_AFTER_MEDIAFILE_REPLACE, mediafile)

    except Exception as e:
        await FileManager.delete(revision_path)
        if thumbnail_filename:
            thumbnail_path = os.path.join(
                cfg.THUMBNAILS_BASE_PATH, thumbnail_filename)
            await FileManager.delete(thumbnail_path)
        raise e

    return {
        "mediafile_id": mediafile.id,
        "revision_id": revision.id,
    }
