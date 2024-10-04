import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.datafile_model import Datafile
from app.models.revision_model import Revision
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.datafile_schemas import DatafileReplaceResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import thumbnail_create
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DATAFILE_REPLACE, HOOK_AFTER_DATAFILE_REPLACE)

cfg = get_config()
router = APIRouter()


@router.post("/datafile/{datafile_id}", summary="Replace a datafile",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DatafileReplaceResponse, tags=["Datafiles"])
@locked
async def datafile_replace(
    datafile_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DatafileReplaceResponse:

    datafile_repository = Repository(session, cache, Datafile)
    datafile = await datafile_repository.select(id=datafile_id)

    if not datafile:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif datafile.is_locked:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
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
            current_user.id, datafile.id, revision_filename,
            os.path.getsize(revision_path), file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # update latest_revision_id
        datafile.latest_revision_id = revision.id
        await datafile_repository.update(datafile, commit=False)

        # # update previous revision
        # revision_repository = Repository(session, cache, Revision)
        # datafile.latest_revision.is_latest = False
        # await revision_repository.update(
        #     datafile.latest_revision, commit=False)

        # update datafile counters and name
        await revision_repository.lock_all()
        datafile.revisions_count = await revision_repository.count_all(
            datafile_id__eq=datafile.id)
        datafile.revisions_size = await revision_repository.sum_all(
            "revision_size", datafile_id__eq=datafile.id)
        datafile.datafile_name = file.filename
        await datafile_repository.update(datafile, commit=False)

        # update collection counters
        if datafile.collection_id:
            await datafile_repository.lock_all()

            datafile.datafile_collection.revisions_count = (
                await datafile_repository.sum_all(
                    "revisions_count",
                    collection_id__eq=datafile.collection_id))

            datafile.datafile_collection.revisions_size = (
                await datafile_repository.sum_all(
                    "revisions_size",
                    collection_id__eq=datafile.collection_id))

            collection_repository = Repository(session, cache, Collection)
            await collection_repository.update(
                datafile.datafile_collection, commit=False)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_DATAFILE_REPLACE, datafile)

        await datafile_repository.commit()
        await hook.do(HOOK_AFTER_DATAFILE_REPLACE, datafile)

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
