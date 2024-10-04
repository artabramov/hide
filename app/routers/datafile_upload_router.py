import os
import uuid
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.datafile_model import Datafile
from app.models.revision_model import Revision
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.datafile_schemas import DatafileUploadResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import thumbnail_create
from app.constants import (
    HOOK_BEFORE_DATAFILE_UPLOAD, HOOK_AFTER_DATAFILE_UPLOAD)

cfg = get_config()
router = APIRouter()


@router.post("/datafile", summary="Upload a new datafile",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DatafileUploadResponse, tags=["Datafiles"])
@locked
async def datafile_upload(
    file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> DatafileUploadResponse:

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
        revision_size = os.path.getsize(revision_path)

        # insert datafile
        datafile_repository = Repository(session, cache, Datafile)
        datafile = Datafile(
            current_user.id, file.filename, revisions_count=1,
            revisions_size=revision_size)
        await datafile_repository.insert(datafile, commit=False)

        # insert revision
        revision_repository = Repository(session, cache, Revision)
        revision = Revision(
            current_user.id, datafile.id, revision_filename, revision_size,
            file.filename, file.size, file.content_type,
            thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # update latest_revision_id
        datafile.latest_revision_id = revision.id
        await datafile_repository.update(datafile, commit=False)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_DATAFILE_UPLOAD, datafile)

        await datafile_repository.commit()
        await hook.do(HOOK_AFTER_DATAFILE_UPLOAD, datafile)

    except Exception as e:
        await FileManager.delete(revision_path)
        if thumbnail_filename:
            thumbnail_path = os.path.join(
                cfg.THUMBNAILS_BASE_PATH, thumbnail_filename)
            await FileManager.delete(thumbnail_path)
        raise e

    return {
        "datafile_id": datafile.id,
        "revision_id": revision.id,
    }
