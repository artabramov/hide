from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.schemas.collection_schemas import (
    CollectionSelectRequest, CollectionSelectResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/collection/{collection_id}", summary="Retrieve collection",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionSelectResponse, tags=["collections"])
async def collection_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CollectionSelectRequest)
) -> CollectionSelectResponse:
    """
    FastAPI router for retrieving a collection entity. The router
    fetches the collection from the repository using the provided ID,
    executes related hooks, and returns the collection details in a JSON
    response. The current user should have a reader role or higher.
    Returns a 200 response on success, a 404 error if the collection is
    not found, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)

    if not collection:
        raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_SELECT, collection)

    return collection.to_dict()
