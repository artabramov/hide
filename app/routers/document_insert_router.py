import os
import uuid
from fastapi import APIRouter, Depends, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.models.document_models import Document
from app.models.revision_models import Revision
from app.schemas.document_schemas import (
    DocumentInsertRequest, DocumentInsertResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.config import get_config
from app.helpers.image_helper import thumbnail_create
from app.libraries.tag_library import TagLibrary
from app.errors import E
from app.schemas.document_schemas import DOCUMENT_NAME_LENGTH

cfg = get_config()
router = APIRouter()


@router.post("/document", summary="Create document",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=DocumentInsertResponse, tags=["documents"])
async def document_insert(
    request: Request,
    file: UploadFile = File(...),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(DocumentInsertRequest)
) -> DocumentInsertResponse:
    """
    FastAPI router for creating a document entity. The router validates
    that the specified collection exists and is not locked, handles the
    file upload including creating a thumbnail and encrypting the file,
    inserts the document and its associated revisions into the
    repository, updates document and collection counters, and executes
    related hooks. Returns the created document ID in a JSON response.
    The current user should have a writer role or higher. Returns a 201
    response on success, a 404 error if the collection is not found,
    a 423 error if the collection is locked, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    # Validate collection
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif collection.is_locked:
        raise E("collection_id", schema.collection_id, E.RESOURCE_LOCKED,
                status_code=status.HTTP_423_LOCKED)

    # Upload file
    revision_filename = str(uuid.uuid4()) + cfg.REVISIONS_EXTENSION
    revision_path = os.path.join(cfg.REVISIONS_BASE_PATH, revision_filename)
    await FileManager.upload(file, revision_path)

    # Create thumbnail
    try:
        mimetype = file.content_type
        thumbnail_filename = await thumbnail_create(revision_path, mimetype)
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

    # Insert document
    if schema.document_name:
        document_name = schema.document_name
    else:
        document_name, _ = os.path.splitext(file.filename)[:DOCUMENT_NAME_LENGTH]  # noqa E501
    document_repository = Repository(session, cache, Document)
    document = Document(current_user.id, schema.collection_id, document_name,
                        document_summary=schema.document_summary)
    await document_repository.insert(document, commit=False)

    # Apply tags
    tag_library = TagLibrary(session, cache)
    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(document.id, tag_values, commit=False)

    # Insert current revision
    revision_repository = Repository(session, cache, Revision)
    revision = Revision(
        current_user.id, document.id, revision_filename,
        os.path.getsize(revision_path), file.filename, file.size,
        file.content_type, thumbnail_filename=thumbnail_filename)
    await revision_repository.insert(revision, commit=False)

    # Update document counters and latest revision
    await revision_repository.lock_all()
    document.document_size = file.size
    document.revisions_count = await revision_repository.count_all(
        document_id__eq=revision.document_id)
    document.revisions_size = await revision_repository.sum_all(
        "revision_size", document_id__eq=revision.document_id)
    await document_repository.update(document, commit=False)

    # Update collection counters
    await document_repository.lock_all()
    collection.documents_count = await document_repository.count_all(
        collection_id__eq=document.collection_id)
    collection.documents_size = await document_repository.sum_all(
        "document_size", collection_id__eq=document.collection_id)
    collection.revisions_count = await document_repository.sum_all(
        "revisions_count", collection_id__eq=document.collection_id)
    collection.revisions_size = await document_repository.sum_all(
        "revisions_size", collection_id__eq=document.collection_id)
    await collection_repository.update(collection, commit=False)

    # Execute hooks
    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_DOCUMENT_INSERT, document)

    await document_repository.commit()
    await hook.execute(H.AFTER_DOCUMENT_INSERT, document)

    return {"document_id": document.id}
