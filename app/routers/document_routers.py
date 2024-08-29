"""
This module provides API endpoints for managing documents. It includes
functionalities for uploading, downloading, updating, and deleting
documents, as well as retrieving detailed information and lists of
documents. The endpoints enforce access controls based on user roles
and handle various aspects of document processing, including file
storage, encryption, and metadata management. The module ensures that
users interact with documents according to their permissions and
maintains the integrity of document-related data throughout different
operations.
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.models.document_models import Document
from app.models.download_models import Download
from app.models.tag_models import Tag
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
from app.managers.entity_manager import SUBQUERY

DOCUMENT_ID = "document_id"

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
    exists and is not locked. Requires the user to have the writer role
    or higher. Returns a 201 response with the ID of the newly created
    document. Returns a 404 error if the collection does not exist, a
    423 error if the collection is locked, and a 403 error if the user's
    token is invalid or if the user lacks the required role.
    """
    # Validate collection
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,  # noqa E501
                status_code=status.HTTP_404_NOT_FOUND)

    elif collection.is_locked:
        raise E("collection_id", schema.collection_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

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
    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(document.id, tag_values)

    # Update counters
    collection.documents_count = await document_repository.count_all(
        collection_id__eq=collection.id)
    collection.documents_size = await document_repository.sum_all(
        "filesize", collection_id__eq=collection.id)
    await collection_repository.update(collection)

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
    Handles the download of a document by returning its raw binary data
    after decryption. Updates the document's download count and records
    the download in the database. Requires the user to have the reader
    role or higher. If the document is not found, raises a 404 error.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise HTTPException(status_code=404)

    data = await FileManager.read(document.file_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(current_user.id, document.id)
    await download_repository.insert(download)

    document.downloads_count = await download_repository.count_all(
        document_id__eq=document.id)
    await document_repository.update(document)

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
    Retrieves details of a specific document by its ID. Requires the
    user to have at least a reader role. Returns the document details
    if found. Raises a 403 error if the user does not have sufficient
    permissions, or a 404 error if the document does not exist.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

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
    """
    Update the details of a specific document. Requires the user to have
    at least an editor role. Checks if the document exists and ensures
    that the collection to which the document is moved is not locked. If
    the collection ID is changed, updates the document and collection
    counters accordingly. Returns the document ID upon successful
    update. Raises a 403 error if the user does not have sufficient
    permissions, a 404 error if the document or collection does not
    exist, and a 423 error if the document or collection is locked,
    and a 422 error if any provided attributes are invalid.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise E("document_id", schema.document_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    if document.document_collection.id != schema.collection_id:
        collection_repository = Repository(session, cache, Collection)
        collection = await collection_repository.select(
            id=schema.collection_id)

        if not collection:
            raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,  # noqa E501
                    status_code=status.HTTP_404_NOT_FOUND)

        if collection.is_locked:
            raise E("collection_id", schema.collection_id, E.RESOURCE_LOCKED,
                    status_code=status.HTTP_423_LOCKED)

    document.collection_id = schema.collection_id
    document.document_name = schema.document_name
    document.document_summary = schema.document_summary
    await document_repository.update(document)

    # Apply tags to document
    tag_library = TagLibrary(session, cache)
    await tag_library.delete_all(document.id)

    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(document.id, tag_values)

    # Update counters when document moved between collections
    if document.document_collection.id != schema.collection_id:
        documents_count = await document_repository.count_all(
            collection_id__eq=document.document_collection.id)
        documents_size = await document_repository.sum_all(
            "filesize", collection_id__eq=document.document_collection.id)
        document.document_collection.documents_count = documents_count
        document.document_collection.documents_size = documents_size
        await collection_repository.update(document.document_collection)

        collection.documents_count = await document_repository.count_all(
            collection_id__eq=collection.id)
        collection.documents_size = await document_repository.sum_all(
            "filesize", collection_id__eq=collection.id)
        await collection_repository.update(collection)

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
    """
    Deletes a specific document by its ID. Requires the user to have an
    admin role. Checks if the document exists and if its collection is
    not locked. If the document is found and the collection is not
    locked, it is removed from the repository, and the collection's
    document counters are updated. Raises a 404 error if the document
    is not found, a 403 error if the collection is locked, and a 422
    error if the attributes are invalid.
    """
    document_repository = Repository(session, cache, Document)

    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise E("document_id", schema.document_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    if document.comments_count > 0:
        # TODO: DO NOT DELETE COMMENTS MANUALLY! DO IT BY ALCHEMY!
        ...

    await document_repository.delete(document)
    await document_repository.commit()

    # Update counters.
    documents_count = await document_repository.count_all(
        collection_id__eq=document.document_collection.id)
    documents_size = await document_repository.sum_all(
        "filesize", collection_id__eq=document.document_collection.id)
    document.document_collection.documents_count = documents_count
    document.document_collection.documentes_size = documents_size

    collection_repository = Repository(session, cache, Collection)
    await collection_repository.update(document.document_collection)

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
    """
    Retrieve a list of documents based on the provided query parameters.
    The user must have at least a reader role. The endpoint dynamically
    prepares query parameters, including any tag filters if specified,
    and fetches the list of documents and their count from the
    repository. It returns a dictionary with the documents and their
    total count.
    """
    document_repository = Repository(session, cache, Document)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await document_repository.entity_manager.subquery(
            Tag, DOCUMENT_ID, tag_value__eq=schema.tag_value__eq)

    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    # hook = Hook(session, cache, request, current_user=current_user)
    # await hook.execute(H.AFTER_COLLECTIONS_LIST, collections)

    return {
        "documents": [document.to_dict() for document in documents],
        "documents_count": documents_count,
    }
