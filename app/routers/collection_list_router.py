from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.schemas.collection_schemas import (
    CollectionListRequest, CollectionListResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/collections", summary="Retrieve collection list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionListResponse, tags=["collections"])
async def collection_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CollectionListRequest)
) -> CollectionListResponse:
    """
    FastAPI router for retrieving a list of collection entities. The
    router fetches the list of collections from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    collection_repository = Repository(session, cache, Collection)

    collections = await collection_repository.select_all(**schema.__dict__)
    collections_count = await collection_repository.count_all(
        **schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_LIST, collections)

    return {
        "collections": [collection.to_dict() for collection in collections],
        "collections_count": collections_count,
    }
