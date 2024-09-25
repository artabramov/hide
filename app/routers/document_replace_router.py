import uuid
import os
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.upload_model import Upload
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.document_schemas import DocumentReplaceResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import thumbnail_create
from app.errors import E
from app.constants import LOC_PATH

cfg = get_config()
router = APIRouter()


@router.post("/document/{document_id}", summary="Replace a document",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentReplaceResponse, tags=["documents"])
@locked
async def document_replace(
    document_id: int, file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentReplaceResponse:

    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                E.ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                E.ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    # upload file
    upload_filename = str(uuid.uuid4()) + cfg.UPLOADS_EXTENSION
    upload_path = os.path.join(cfg.UPLOADS_BASE_PATH, upload_filename)
    await FileManager.upload(file, upload_path)

    # create thumbnail
    thumbnail_filename = None
    try:
        mimetype = file.content_type
        thumbnail_filename = await thumbnail_create(upload_path, mimetype)
    except Exception:
        pass

    try:
        # encrypt file
        data = await FileManager.read(upload_path)
        encrypted_data = await FileManager.encrypt(data)
        await FileManager.write(upload_path, encrypted_data)

        # insert upload
        upload_repository = Repository(session, cache, Upload)
        upload = Upload(
            current_user.id, document.id, upload_filename,
            os.path.getsize(upload_path), file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await upload_repository.insert(upload, commit=False)

        # update previous upload
        upload_repository = Repository(session, cache, Upload)
        document.latest_upload.is_latest = False
        await upload_repository.update(document.latest_upload, commit=False)

        # update document counters and name
        await upload_repository.lock_all()
        document.uploads_count = await upload_repository.count_all(
            document_id__eq=document.id)
        document.uploads_size = await upload_repository.sum_all(
            "upload_size", document_id__eq=document.id)
        document.document_name = file.filename
        await document_repository.update(document, commit=False)

        # update collection counters
        if document.collection_id:
            await document_repository.lock_all()

            document.document_collection.uploads_count = (
                await document_repository.sum_all(
                    "uploads_count", collection_id__eq=document.collection_id))

            document.document_collection.uploads_size = (
                await document_repository.sum_all(
                    "uploads_size", collection_id__eq=document.collection_id))

            collection_repository = Repository(session, cache, Collection)
            await collection_repository.update(
                document.document_collection, commit=False)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(H.BEFORE_DOCUMENT_REPLACE, document)

        await document_repository.commit()
        await hook.do(H.AFTER_DOCUMENT_REPLACE, document)

    except Exception as e:
        await FileManager.delete(upload_path)
        if thumbnail_filename:
            thumbnail_path = os.path.join(
                cfg.THUMBNAILS_BASE_PATH, thumbnail_filename)
            await FileManager.delete(thumbnail_path)
        raise e

    return {
        "document_id": document.id,
        "upload_id": upload.id,
    }
