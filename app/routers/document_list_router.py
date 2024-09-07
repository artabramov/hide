from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.tag_models import Tag
from app.schemas.document_schemas import (
    DocumentListRequest, DocumentListResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.entity_manager import SUBQUERY

router = APIRouter()


@router.get("/documents", summary="Retrieve document list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentListResponse, tags=["documents"])
async def document_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(DocumentListRequest)
) -> DocumentListResponse:
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
