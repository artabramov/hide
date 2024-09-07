from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.models.document_models import Document
from app.schemas.document_schemas import (
    DocumentDeleteRequest, DocumentDeleteResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E

router = APIRouter()


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
