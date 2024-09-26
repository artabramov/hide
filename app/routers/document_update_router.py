from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.models.upload_model import Upload
from app.schemas.document_schemas import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.libraries.tag_library import TagLibrary
from app.errors import E
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DOCUMENT_UPDATE, HOOK_AFTER_DOCUMENT_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}",
            summary="Update a document",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentUpdateResponse, tags=["documents"])
@locked
async def document_update(
    document_id: int, schema: DocumentUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentUpdateResponse:

    # Validate the document.

    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    # If a collection ID is received, then validate the collection.

    collection = None
    if schema.collection_id:
        collection_repository = Repository(session, cache, Collection)
        collection = await collection_repository.select(
            id=schema.collection_id)

        if not collection:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        elif collection.is_locked:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    # Update the data of the document itself.

    document.collection_id = schema.collection_id
    document.document_name = schema.document_name
    document.document_summary = schema.document_summary
    await document_repository.update(document, commit=False)

    # If a collection ID is received, then update
    # the collection's counters.

    if collection:
        await document_repository.lock_all()

        collection.documents_count = await document_repository.count_all(
            collection_id__eq=collection.id)

        collection.uploads_count = await document_repository.sum_all(
            "uploads_count", collection_id__eq=collection.id)

        collection.uploads_size = await document_repository.sum_all(
            "uploads_size", collection_id__eq=collection.id)

        await collection_repository.update(collection, commit=False)

    # If the document already has a related collection,
    # then update the collection's counters.

    if document.document_collection:
        await document_repository.lock_all()

        document.document_collection.documents_count = (
            await document_repository.count_all(
                collection_id__eq=document.document_collection.id))

        document.document_collection.uploads_count = (
            await document_repository.sum_all(
                "uploads_count",
                collection_id__eq=document.document_collection.id))

        document.document_collection.uploads_size = (
            await document_repository.sum_all(
                "uploads_size",
                collection_id__eq=document.document_collection.id))

        await collection_repository.update(
            document.document_collection, commit=False)

    # Update the original filename for the latest upload
    # associated with the document.

    if document.latest_upload.original_filename != document.document_name:
        document.latest_upload.original_filename = document.document_name

        upload_repository = Repository(session, cache, Upload)
        await upload_repository.update(document.latest_upload, commit=False)

    # Update tags associated with the document.

    tag_library = TagLibrary(session, cache)
    await tag_library.delete_all(document.id, commit=False)

    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(document.id, tag_values, commit=False)

    # Execute the corresponding hooks before and
    # after committing the changes

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_UPDATE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
        "upload_id": document.latest_upload.id,
    }
