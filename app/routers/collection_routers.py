from fastapi import APIRouter, Depends, Request, HTTPException, status
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.schemas.collection_schemas import (
    CollectionInsertRequest, CollectionInsertResponse,  CollectionSelectRequest,
    CollectionSelectResponse, CollectionUpdateRequest, CollectionUpdateResponse,
    CollectionDeleteRequest, CollectionDeleteResponse, CollectionsListRequest,
    CollectionsListResponse)
from app.repository import Repository
from app.errors import E, Msg
from app.config import get_config
from app.hooks import HookAction, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/collection", response_model=CollectionInsertResponse,
             tags=["collections"], name="Create an collection")
async def collection_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(CollectionInsertRequest)
) -> dict:
    """
    Create a new collection if it does not already exist. Requires the user
    to have the writer role or higher. Checks if an collection with the same
    name exists, raising an error if it does. Otherwise, creates the
    collection with the provided details and returns its ID.
    """
    collection_repository = Repository(session, cache, Collection)

    collection_exists = await collection_repository.exists(
        collection_name__eq=schema.collection_name)

    if collection_exists:
        raise E("collection_name", schema.collection_name, Msg.COLLECTION_NAME_EXISTS)

    collection = Collection(current_user.id, schema.is_locked, schema.collection_name,
                  collection_summary=schema.collection_summary)
    await collection_repository.insert(collection)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(HookAction.after_collection_insert, collection)

    return {"collection_id": collection.id}


@router.get("/collection/{collection_id}", response_model=CollectionSelectResponse,
            tags=["collections"], name="Retrieve an collection")
async def collection_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CollectionSelectRequest)
) -> dict:
    """
    Retrieve an collection by its ID. Returns the collection details if found;
    otherwise, raises a 404 error. Requires the user to have the reader
    role or higher.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(HookAction.after_collection_select, collection)

    return collection.to_dict()


@router.put("/collection/{collection_id}", response_model=CollectionUpdateResponse,
            tags=["collections"], name="Update an collection")
async def collection_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CollectionUpdateRequest)
) -> dict:
    """
    Update an existing collection's details by its ID. Requires editor role
    or higher. Raises an error if the collection is not found or if the new
    name conflicts with an existing collection name. Returns the ID of the
    updated collection.
    """
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    collection_exists = await collection_repository.exists(
        collection_name__eq=schema.collection_name, id__ne=collection.id)
    if collection_exists:
        raise E("collection_name", schema.collection_name, Msg.COLLECTION_NAME_EXISTS)

    collection.is_locked = schema.is_locked
    collection.collection_name = schema.collection_name
    collection.collection_summary = schema.collection_summary
    await collection_repository.update(collection)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(HookAction.after_collection_update, collection)

    return {"collection_id": collection.id}


@router.delete("/collection/{collection_id}", response_model=CollectionDeleteResponse,
               tags=["collections"], name="Delete an collection")
async def collection_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(CollectionDeleteRequest)
) -> dict:
    """
    Delete an collection by its ID from the repository. Requires admin role.
    Raises a 404 error if the collection is not found. Deletes related posts
    if any exist. Returns the ID of the deleted collection.
    """
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if collection.posts_count > 0:
        # TODO: delete related posts
        ...

    await collection_repository.delete(collection, commit=False)
    await collection_repository.commit()

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(HookAction.after_collection_delete, collection)

    return {"collection_id": collection.id}


@router.get("/collections", response_model=CollectionsListResponse, tags=["collections"],
            name="Retrieve collections list")
async def collections_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CollectionsListRequest)
) -> dict:
    """
    Retrieve a list of collections based on the provided query parameters.
    Returns the list of collections and the total count. If no collections are
    found, an empty list and zero count are returned. Requires reader
    role or higher.
    """
    collection_repository = Repository(session, cache, Collection)

    collections = await collection_repository.select_all(**schema.__dict__)
    collections_count = await collection_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(HookAction.after_collections_list, collections)

    return {
        "collections": [collection.to_dict() for collection in collections],
        "collections_count": collections_count,
    }
