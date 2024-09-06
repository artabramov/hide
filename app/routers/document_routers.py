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


@router.get("/document/{document_id}", summary="Retrieve document",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentSelectResponse, tags=["documents"])
async def document_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentSelectRequest)
) -> DocumentSelectResponse:
    """
    FastAPI router for retrieving a document entity. The router fetches
    the document from the repository using the provided ID, verifies
    that the document exists, executes related hooks, and returns the
    document details in a JSON response. The current user should have
    a reader role or higher. Returns a 200 response on success, a 404
    error if the document is not found, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_SELECT, document)

    return document.to_dict()


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


@router.delete("/document/{document_id}", summary="Delete document",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=DocumentDeleteResponse, tags=["documents"])
async def document_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(DocumentDeleteRequest)
) -> DocumentDeleteResponse:
    """
    FastAPI router for deleting a document entity. The router retrieves
    the document from the repository using the provided ID, checks if
    the document exists and its collection is not locked, deletes the
    document and all related entities, updates the counters for the
    associated collection, executes related hooks, and returns the
    deleted document ID in a JSON response. The current user should
    have an admin role. Returns a 200 response on success, a 404 error
    if the document is not found, a 423 error if the collection is
    locked, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    document_repository = Repository(session, cache, Document)

    document = await document_repository.select(id=schema.document_id)
    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif document.document_collection.is_locked:
        raise E("document_id", schema.document_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    await document_repository.delete(document, commit=False)

    # Update counters.
    # document.document_collection.documents_count = await document_repository.count_all(  # noqa E501
    #     collection_id__eq=document.document_collection.id)
    # document.document_collection.documentes_size = await document_repository.sum_all(  # noqa E501
    #     "filesize", collection_id__eq=document.document_collection.id)

    collection_repository = Repository(session, cache, Collection)
    await collection_repository.update(document.document_collection,
                                       commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_DOCUMENT_DELETE, document)

    await document_repository.commit()
    await hook.execute(H.AFTER_DOCUMENT_DELETE, document)

    return {"document_id": document.id}


@router.get("/documents", summary="Retrieve document list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentsListResponse, tags=["documents"])
async def document_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentsListRequest)
) -> DocumentsListResponse:
    """
    FastAPI router for retrieving a list of document entities. The
    router fetches the list of documents from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    document_repository = Repository(session, cache, Document)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await document_repository.entity_manager.subquery(
            Tag, "document_id", tag_value__eq=schema.tag_value__eq)

    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_LIST, documents)

    return {
        "documents": [document.to_dict() for document in documents],
        "documents_count": documents_count,
    }
