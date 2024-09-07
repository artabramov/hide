import os
import uuid
from fastapi import APIRouter, Depends, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.schemas.document_schemas import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.config import get_config
from app.helpers.image_helper import thumbnail_create
from app.libraries.tag_library import TagLibrary
from app.errors import E

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}", summary="Update document",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentUpdateResponse, tags=["documents"])
async def document_update(
    request: Request,
    file: UploadFile = File(None),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(DocumentUpdateRequest)
) -> DocumentUpdateResponse:
    """
    FastAPI router for updating a document entity. The router fetches
    the document from the repository using the provided ID, verifies
    that the document exists and its collection is not locked, updates
    the document's tags, processes any uploaded file by creating a new
    revision. It then updates counters for both the document and its
    collection, executes related hooks, and returns the updated document
    ID in a JSON response. The current user should have an editor role
    or higher. Returns a 200 response on success, a 404 error if the
    document or collection is not found, a 423 error if the collection
    is locked, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = None

    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise E("document_id", schema.document_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    if document.document_collection.id != schema.collection_id:
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
    await document_repository.update(document, commit=False)

    # Apply tags
    tag_library = TagLibrary(session, cache)
    await tag_library.delete_all(document.id, commit=False)
    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(document.id, tag_values, commit=False)

    if file:
        # Upload file
        revision_filename = str(uuid.uuid4()) + cfg.REVISIONS_EXTENSION
        revision_path = os.path.join(cfg.REVISIONS_BASE_PATH, revision_filename)  # noqa E501
        await FileManager.upload(file, revision_path)

        # Create thumbnail
        try:
            mimetype = file.content_type
            thumbnail_filename = await thumbnail_create(revision_path, mimetype)  # noqa E501
        except Exception:
            pass

        # Encrypt file
        try:
            data = await FileManager.read(revision_path)
            encrypted_data = await FileManager.encrypt(data)
            await FileManager.write(revision_path, encrypted_data)
        except Exception as e:
            await FileManager.delete(revision_path)
            raise e

        # Unset previous revision
        revision_repository = Repository(session, cache, Revision)
        previous_revision = await revision_repository.select(
            document_id__eq=document.id, is_latest__eq=True)
        previous_revision.is_latest = False
        await revision_repository.update(previous_revision, commit=False)

        # Set current revision
        revision = Revision(
            current_user.id, document.id, revision_filename,
            os.path.getsize(revision_path), file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # Update document counters and latest revision
        document.document_size = file.size
        await revision_repository.lock_all()
        document.revisions_count = await revision_repository.count_all(
            document_id__eq=revision.document_id)
        document.revisions_size = await revision_repository.sum_all(
            "revision_size", document_id__eq=revision.document_id)
        await document_repository.update(document, commit=False)

    # Update current collection counters
    if collection or file:
        await document_repository.lock_all()
        doc_collection = document.document_collection
        doc_collection.documents_count = await document_repository.count_all(
            collection_id__eq=doc_collection.id)
        doc_collection.documents_size = await document_repository.sum_all(
            "document_size", collection_id__eq=doc_collection.id)
        doc_collection.revisions_count = await document_repository.sum_all(
            "revisions_count", collection_id__eq=doc_collection.id)
        doc_collection.revisions_size = await document_repository.sum_all(
            "revisions_size", collection_id__eq=doc_collection.id)
        await collection_repository.update(doc_collection, commit=False)

    # Update new collection counters
    if collection:
        collection.documents_count = await document_repository.count_all(
            collection_id__eq=collection.id)
        collection.documents_size = await document_repository.sum_all(
            "document_size", collection_id__eq=collection.id)
        collection.revisions_count = await document_repository.sum_all(
            "revisions_count", collection_id__eq=collection.id)
        collection.revisions_size = await document_repository.sum_all(
            "revisions_size", collection_id__eq=collection.id)
        await collection_repository.update(collection, commit=False)

    # Execute hooks
    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_DOCUMENT_UPDATE, document)

    await document_repository.commit()
    await hook.execute(H.AFTER_DOCUMENT_UPDATE, document)

    return {"document_id": document.id}
