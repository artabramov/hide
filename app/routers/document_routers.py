import uuid
import os
from time import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.schemas.document_schemas import (
    DocumentUploadRequest, DocumentUploadResponse)
from app.errors import E, Msg
from app.hooks import HookAction, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import ImageHelper
from app.config import get_config
from app.models.document_model import Document

router = APIRouter()
cfg = get_config()


@router.post("/document", response_model=DocumentUploadResponse,
             tags=["documents"], name="Upload document")
async def document_upload(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(DocumentUploadRequest)
) -> dict:
    """
    Upload a new document to the specified collection. Ensures the collection exists
    and the user has the writer role or higher before proceeding
    with the upload.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user_id = current_user.id
    collection_id = schema.collection_id

    original_filename = schema.file.filename
    document_filename = str(uuid.uuid4())
    document_path = os.path.join(cfg.DOCUMENTS_BASE_PATH, document_filename)
    document_filesize = schema.file.size
    document_mimetype = schema.file.content_type
    document_width = 0
    document_height = 0
    document_duration = 0
    document_bitrate = 0
    document_summary = schema.document_summary

    thumbnail_filename = None

    await FileManager.upload(schema.file, document_path)

    document_repository = Repository(session, cache, Document)
    document = Document(user_id, collection_id, original_filename, document_filename,
                document_filesize, document_mimetype, document_width, document_height,
                document_duration, document_bitrate, document_summary, thumbnail_filename)
    await document_repository.insert(document)

    # hook = Hook(session, cache, request, current_user=current_user)
    # await hook.execute(HookAction.after_userpic_upload, current_user)

    return {
        "document_id": document.id
    }
