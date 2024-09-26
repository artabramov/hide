import os
import uuid
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.upload_model import Upload
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.document_schemas import DocumentUploadResponse
from app.managers.file_manager import FileManager
from app.helpers.image_helper import thumbnail_create
from app.constants import (
    HOOK_BEFORE_DOCUMENT_UPLOAD, HOOK_AFTER_DOCUMENT_UPLOAD)

cfg = get_config()
router = APIRouter()


@router.post("/document", summary="Upload a new document",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentUploadResponse, tags=["documents"])
@locked
async def document_upload(
    file: UploadFile = File(...),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> DocumentUploadResponse:

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
        upload_size = os.path.getsize(upload_path)

        # insert document
        document_repository = Repository(session, cache, Document)
        document = Document(current_user.id, file.filename, uploads_count=1,
                            uploads_size=upload_size)
        await document_repository.insert(document, commit=False)

        # insert upload
        upload_repository = Repository(session, cache, Upload)
        upload = Upload(
            current_user.id, document.id, upload_filename, upload_size,
            file.filename, file.size, file.content_type,
            thumbnail_filename=thumbnail_filename)
        await upload_repository.insert(upload, commit=False)

        # execute hooks
        hook = Hook(session, cache, current_user=current_user)
        await hook.do(HOOK_BEFORE_DOCUMENT_UPLOAD, document)

        await document_repository.commit()
        await hook.do(HOOK_AFTER_DOCUMENT_UPLOAD, document)

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
