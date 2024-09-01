from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.collection_models import Collection
from app.schemas.collection_schemas import (
    CollectionInsertRequest, CollectionInsertResponse,
    CollectionSelectRequest, CollectionSelectResponse,
    CollectionUpdateRequest, CollectionUpdateResponse,
    CollectionDeleteRequest, CollectionDeleteResponse,
    CollectionsListRequest, CollectionsListResponse)
from app.repository import Repository
from app.errors import E
from app.config import get_config
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/collection", name="Create collection",
             tags=["collections"], response_model=CollectionInsertResponse)
async def collection_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer)),
    schema=Depends(CollectionInsertRequest)
) -> dict:
    collection_repository = Repository(session, cache, Collection)

    collection_exists = await collection_repository.exists(
        collection_name__eq=schema.collection_name)

    if collection_exists:
        raise E("collection_name", schema.collection_name, E.VALUE_DUPLICATED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection = Collection(
        current_user.id, schema.is_locked, schema.collection_name,
        collection_summary=schema.collection_summary)
    await collection_repository.insert(collection)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_INSERT, collection)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"collection_id": collection.id}
    )


@router.get("/collection/{collection_id}", name="Retrieve collection",
            tags=["collections"], response_model=CollectionSelectResponse)
async def collection_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CollectionSelectRequest)
) -> dict:
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=schema.collection_id)

    if not collection:
        raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_SELECT, collection)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=collection.to_dict()
    )


@router.put("/collection/{collection_id}", name="Update collection",
            tags=["collections"], response_model=CollectionUpdateResponse)
async def collection_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor)),
    schema=Depends(CollectionUpdateRequest)
) -> dict:
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
    await collection_repository.update(collection)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_UPDATE, collection)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"collection_id": collection.id}
    )


@router.delete("/collection/{collection_id}", name="Delete collection",
               tags=["collections"], response_model=CollectionDeleteResponse)
async def collection_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(CollectionDeleteRequest)
) -> dict:
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=schema.collection_id)
    if not collection:
        raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    if collection.documents_count > 0:
        # TODO: delete related documents
        ...

    await collection_repository.delete(collection, commit=False)
    await collection_repository.commit()

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTION_DELETE, collection)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"collection_id": collection.id}
    )


@router.get("/collections", name="Collections list",
            tags=["collections"], response_model=CollectionsListResponse)
async def collections_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(CollectionsListRequest)
) -> dict:
    collection_repository = Repository(session, cache, Collection)

    collections = await collection_repository.select_all(**schema.__dict__)
    collections_count = await collection_repository.count_all(
        **schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_COLLECTIONS_LIST, collections)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "collections": [collection.to_dict() for collection in collections],  # noqa E501
            "collections_count": collections_count,
        }
    )
