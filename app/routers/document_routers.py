import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.models.document_model import Document
from app.schemas.document_schemas import (
    DocumentUploadRequest, DocumentUploadResponse, DocumentDownloadRequest)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.config import get_config

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
    Upload a new document to the specified collection. Ensures the
    collection exists and the user has the writer role or higher
    before proceeding with the upload.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    elif collection.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    filename = str(uuid.uuid4()) + cfg.DOCUMENTS_EXTENSION
    path = os.path.join(cfg.DOCUMENTS_BASE_PATH, filename)
    await FileManager.upload(schema.file, path)

    data = await FileManager.read(path)
    encrypted_data = await FileManager.encrypt(data)
    await FileManager.write(path, encrypted_data)

    document_name = (schema.document_name if schema.document_name
                     else schema.file.filename)
    document_summary = schema.document_summary
    filesize = schema.file.size
    mimetype = schema.file.content_type
    thumbnail_filename = None

    document_repository = Repository(session, cache, Document)
    document = Document(
        current_user.id, schema.collection_id, document_name, filename,
        filesize, mimetype, document_summary=document_summary,
        thumbnail_filename=thumbnail_filename)
    await document_repository.insert(document)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_INSERT, document)

    return {
        "document_id": document.id
    }


@router.get("/document/{document_id}/download", tags=["documents"],
            name="Download document")
async def document_download(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentDownloadRequest)
) -> Response:
    """
    Returns the raw binary data of the file specified by the
    document ID. The file is decrypted before being sent to the client.
    The user has the reader role or higher before proceeding with the
    download.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise HTTPException(status_code=404)

    data = await FileManager.read(document.file_path)
    decrypted_data = await FileManager.decrypt(data)
    return Response(content=decrypted_data, media_type=document.mimetype)
