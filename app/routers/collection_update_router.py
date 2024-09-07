from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_schemas import (
    CollectionUpdateRequest, CollectionUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.put("/collection/{collection_id}", summary="Update collection",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionUpdateResponse, tags=["collections"])
async def collection_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CollectionUpdateRequest)
) -> CollectionUpdateResponse:
    """
    FastAPI router for updating a collection entity. The router
    retrieves the collection from the repository using the provided ID,
    ensures that the collection exists, and checks that the new
    collection name is unique. It updates the collection's attributes,
    executes related hooks, and returns the updated collection ID in
    a JSON response. The current user should have an editor role or
    higher. Returns a 200 response on success, a 404 error if the
    collection is not found, a 422 error if the collection name is
    duplicated, and a 403 error if authentication fails or the user
    does not have the required role.
    """
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    collection_exists = await collection_repository.exists(
        collection_name__eq=schema.collection_name, id__ne=collection.id)
    if collection_exists:
        raise E("collection_name", schema.collection_name, E.VALUE_DUPLICATED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection.is_locked = schema.is_locked
    collection.collection_name = schema.collection_name
    collection.collection_summary = schema.collection_summary
    await collection_repository.update(collection, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_COLLECTION_UPDATE, collection)

    await collection_repository.commit()
    await hook.execute(H.AFTER_COLLECTION_UPDATE, collection)

    return {"collection_id": collection.id}
