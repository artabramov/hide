from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.schemas.document_schemas import (
    DocumentSelectRequest, DocumentSelectResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E

router = APIRouter()


@router.get("/document/{document_id}", summary="Retrieve document",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentSelectResponse, tags=["documents"])
@locked
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
