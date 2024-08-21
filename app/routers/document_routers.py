import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.models.document_model import Document
from app.schemas.document_schemas import (
    DocumentUploadRequest, DocumentUploadResponse, DocumentDownloadRequest,
    DocumentSelectRequest, DocumentSelectResponse, DocumentDeleteRequest,
    DocumentDeleteResponse, DocumentsListRequest, DocumentsListResponse,
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.config import get_config
from app.helpers.image_helper import image_resize
from app.helpers.video_helper import video_freeze
from app.libraries.tag_library import TagLibrary
from app.errors import E

cfg = get_config()
router = APIRouter()


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
    Handles the upload of a document, including validation, file
    processing, and storage. Validates that the specified collection
    exists and is not locked, checks that the current user has the
    necessary permissions, and saves the uploaded file with a unique
    filename. Generates a thumbnail if the file is an image or video,
    encrypts the file, and creates an entry in the document repository
    with metadata including name, size, MIME type, and optional summary.
    Tags are applied to the document, and a post-upload hook is
    triggered. Returns the ID of the newly created document.
    """

    # Validate collection
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    elif collection.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Save uploaded file
    filename = str(uuid.uuid4()) + cfg.DOCUMENTS_EXTENSION
    file_path = os.path.join(cfg.DOCUMENTS_BASE_PATH, filename)
    await FileManager.upload(schema.file, file_path)

    # Generate thumbnail if applicable
    mimetype = schema.file.content_type
    is_image = FileManager.is_image(mimetype)
    is_video = FileManager.is_video(mimetype) if not is_image else False

    thumbnail_filename = None
    if is_image or is_video:

        thumbnail_filename = str(uuid.uuid4()) + cfg.THUMBNAILS_EXTENSION
        thumbnail_path = os.path.join(
            cfg.THUMBNAILS_BASE_PATH, thumbnail_filename)

        try:
            if is_image:
                await FileManager.copy(file_path, thumbnail_path)

            elif is_video:
                await video_freeze(file_path, thumbnail_path)

            await image_resize(thumbnail_path, cfg.THUMBNAIL_WIDTH,
                               cfg.THUMBNAIL_HEIGHT, cfg.THUMBNAIL_QUALITY)

        except Exception:
            thumbnail_filename = None

    # Encrypt file
    data = await FileManager.read(file_path)
    encrypted_data = await FileManager.encrypt(data)
    await FileManager.write(file_path, encrypted_data)

    # Insert document SQLAlchemy model
    document_name = (schema.document_name if schema.document_name
                     else schema.file.filename)
    document_summary = schema.document_summary
    filesize = schema.file.size

    document_repository = Repository(session, cache, Document)
    document = Document(
        current_user.id, schema.collection_id, document_name, filename,
        filesize, mimetype, document_summary=document_summary,
        thumbnail_filename=thumbnail_filename)
    await document_repository.insert(document)

    # Apply tags to document
    tag_library = TagLibrary(session, cache)
    tag_values = tag_library.extract(schema.tags)
    await tag_library.insert_all(document.id, tag_values)

    # Execute post-upload hook
    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_UPLOAD, document)

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

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_DOWNLOAD, document)

    return Response(content=decrypted_data, media_type=document.mimetype)


@router.get("/document/{document_id}", name="Retrieve a document",
            tags=["documents"], response_model=DocumentSelectResponse)
async def document_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentSelectRequest)
) -> dict:
    """
    Retrieves details of a specific document by its ID. Validates the
    user's access permissions to ensure they have at least a reader
    role. Fetches the document from the repository and, if found,
    triggers a hook for any post-retrieval actions. Returns the document
    details in a dictionary format. Raises a 404 error if the document
    does not exist.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_SELECT, document)

    return document.to_dict()


@router.put("/document/{document_id}", name="Update a document",
            tags=["documents"], response_model=DocumentUpdateResponse)
async def document_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(DocumentUpdateRequest)
) -> dict:
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise E("document_id", schema.document_id, E.NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise E("document_id", schema.document_id, E.LOCKED,
                status_code=status.HTTP_423_LOCKED)

    if document.document_collection.id != schema.collection_id:
        collection_repository = Repository(session, cache, Collection)
        collection = await collection_repository.select(
            id=schema.collection_id)

        if not collection:
            raise E("collection_id", schema.collection_id, E.NOT_FOUND,
                    status_code=status.HTTP_404_NOT_FOUND)

        if collection.is_locked:
            raise E("collection_id", schema.collection_id, E.LOCKED,
                    status_code=status.HTTP_423_LOCKED)

    document.collection_id = schema.collection_id
    document.document_name = schema.document_name
    document.document_summary = schema.document_summary
    await document_repository.update(document)

    # Apply tags to document
    tag_library = TagLibrary(session, cache)
    tag_values = tag_library.extract(schema.tags)
    await tag_library.delete_all(document.id)
    await tag_library.insert_all(document.id, tag_values)

    # TODO: update counters

    # hook = Hook(session, cache, request, current_user=current_user)
    # await hook.execute(H.AFTER_COLLECTION_UPDATE, collection)

    return {"document_id": document.id}


@router.delete("/document/{document_id}", name="Delete a document",
               tags=["documents"], response_model=DocumentDeleteResponse)
async def document_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(DocumentDeleteRequest)
) -> dict:
    document_repository = Repository(session, cache, Document)

    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if document.comments_count > 0:
        # TODO: delete related comments
        ...

    # Delete tags
    # tag_library = TagLibrary(session, cache)
    # await tag_library.delete_all(document.id)

    # await document_repository.delete(document, commit=False)
    # await document_repository.commit()

    # hook = Hook(session, cache, request, current_user=current_user)
    # await hook.execute(H.AFTER_COLLECTION_DELETE, collection)

    return {"document_id": document.id}


@router.get("/documents", name="Retrieve documents list",
            tags=["documents"], response_model=DocumentsListResponse)
async def documents_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentsListRequest)
) -> dict:
    document_repository = Repository(session, cache, Document)

    documents = await document_repository.select_all(**schema.__dict__)
    documents_count = await document_repository.count_all(
        **schema.__dict__)

    # hook = Hook(session, cache, request, current_user=current_user)
    # await hook.execute(H.AFTER_COLLECTIONS_LIST, collections)

    return {
        "documents": [document.to_dict() for document in documents],
        "documents_count": documents_count,
    }
