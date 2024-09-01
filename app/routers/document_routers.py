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
from app.models.tag_models import Tag
from app.schemas.document_schemas import (
    DocumentInsertRequest, DocumentInsertResponse, DocumentSelectRequest,
    DocumentSelectResponse, DocumentDeleteRequest, DocumentDeleteResponse,
    DocumentsListRequest, DocumentsListResponse, DocumentUpdateRequest,
    DocumentUpdateResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.config import get_config
from app.helpers.image_helper import thumbnail_create
from app.libraries.tag_library import TagLibrary
from app.errors import E
from app.managers.entity_manager import SUBQUERY
from app.schemas.document_schemas import DOCUMENT_NAME_LENGTH

cfg = get_config()
router = APIRouter()


@router.post("/document", response_model=DocumentInsertResponse,
             tags=["documents"], name="Upload document")
async def document_insert(
    request: Request,
    file: UploadFile = File(...),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(DocumentInsertRequest)
) -> dict:
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
    upload_path = os.path.join(cfg.REVISIONS_BASE_PATH, revision_filename)
    await FileManager.upload(file, upload_path)

    # Create thumbnail
    mimetype = file.content_type
    thumbnail_filename = await thumbnail_create(upload_path, mimetype)

    # Encrypt file
    data = await FileManager.read(upload_path)
    encrypted_data = await FileManager.encrypt(data)
    await FileManager.write(upload_path, encrypted_data)

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

    # Insert revision
    revision_repository = Repository(session, cache, Revision)
    revision = Revision(
        current_user.id, document.id, revision_filename,
        os.path.getsize(upload_path), file.filename, file.size,
        file.content_type, thumbnail_filename=thumbnail_filename)
    await revision_repository.insert(revision, commit=False)

    # Update document revision and counters
    await revision_repository.lock_all()
    document.last_revision_id = revision.id
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

    # # Execute hooks
    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_INSERT, document)

    await document_repository.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"document_id": document.id}
    )


@router.get("/document/{document_id}", name="Retrieve a document",
            tags=["documents"], response_model=DocumentSelectResponse)
async def document_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentSelectRequest)
) -> dict:
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_SELECT, document)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=document.to_dict()
    )


@router.put("/document/{document_id}", name="Update a document",
            tags=["documents"], response_model=DocumentUpdateResponse)
async def document_update(
    request: Request,
    file: UploadFile = File(None),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(DocumentUpdateRequest)
) -> dict:
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
        upload_path = os.path.join(cfg.REVISIONS_BASE_PATH, revision_filename)
        await FileManager.upload(file, upload_path)

        # Create thumbnail
        mimetype = file.content_type
        thumbnail_filename = await thumbnail_create(upload_path, mimetype)

        # Encrypt file
        data = await FileManager.read(upload_path)
        encrypted_data = await FileManager.encrypt(data)
        await FileManager.write(upload_path, encrypted_data)

        # Insert revision
        revision_repository = Repository(session, cache, Revision)
        revision = Revision(
            current_user.id, document.id, revision_filename,
            os.path.getsize(upload_path), file.filename, file.size,
            file.content_type, thumbnail_filename=thumbnail_filename)
        await revision_repository.insert(revision, commit=False)

        # Update document revision and counters
        await revision_repository.lock_all()
        document.last_revision_id = revision.id
        document.document_size = file.size
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

    await document_repository.commit()

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_UPDATE, document)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"document_id": document.id}
    )


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

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_DELETE, document)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"document_id": document.id}
    )


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

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await document_repository.entity_manager.subquery(
            Tag, "document_id", tag_value__eq=schema.tag_value__eq)

    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENTS_LIST, documents)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "documents": [document.to_dict() for document in documents],
            "documents_count": documents_count,
        }
    )
