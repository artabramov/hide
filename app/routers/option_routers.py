from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.option_models import Option
from app.schemas.option_schemas import (
    OptionInsertRequest, OptionInsertResponse,)
from app.repository import Repository
from app.errors import E
from app.config import get_config
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/option", name="Create option",
             tags=["options"], response_model=OptionInsertResponse)
async def option_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(OptionInsertRequest)
) -> dict:
    option_repository = Repository(session, cache, Option)

    option_exists = await option_repository.exists(
        option_key__eq=schema.option_key)

    if option_exists:
        raise E("option_key", schema.option_key, E.VALUE_DUPLICATED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    option = Option(current_user.id, schema.option_key, schema.option_value)
    await option_repository.insert(option, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_COLLECTION_INSERT, collection)

    await collection_repository.commit()
    await hook.execute(H.AFTER_COLLECTION_INSERT, collection)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"collection_id": collection.id}
    )


# @router.get("/collection/{collection_id}", name="Retrieve collection",
#             tags=["collections"], response_model=CollectionSelectResponse)
# async def collection_select(
#     request: Request,
#     session=Depends(get_session),
#     cache=Depends(get_cache),
#     current_user: User = Depends(auth(UserRole.reader)),
#     schema=Depends(CollectionSelectRequest)
# ) -> dict:
#     """
#     Retrieve a collection entity by its ID. The router fetches the
#     collection from the repository using the provided ID, executes
#     related hooks, and returns the collection details in a JSON response.
#     The current user should have a reader role or higher. Returns a 200
#     response on success, a 404 error if the collection is not found, and
#     a 403 error if authentication fails or the user does not have the
#     required role.
#     """
#     collection_repository = Repository(session, cache, Collection)
#     collection = await collection_repository.select(id=schema.collection_id)

#     if not collection:
#         raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
#                 status_code=status.HTTP_404_NOT_FOUND)

#     hook = Hook(session, cache, request, current_user=current_user)
#     await hook.execute(H.AFTER_COLLECTION_SELECT, collection)

#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content=collection.to_dict()
#     )


# @router.put("/collection/{collection_id}", name="Update collection",
#             tags=["collections"], response_model=CollectionUpdateResponse)
# async def collection_update(
#     request: Request,
#     session=Depends(get_session),
#     cache=Depends(get_cache),
#     current_user: User = Depends(auth(UserRole.editor)),
#     schema=Depends(CollectionUpdateRequest)
# ) -> dict:
#     """
#     Update a collection entity by its ID. The router retrieves the
#     collection from the repository using the provided ID, ensures that
#     the collection exists, and checks that the new collection name is
#     unique. It updates the collection's attributes, executes related
#     hooks, and returns the updated collection ID in a JSON response.
#     The current user should have an editor role or higher. Returns a 200
#     response on success, a 404 error if the collection is not found,
#     a 422 error if the collection name is duplicated, and a 403 error if
#     authentication fails or the user does not have the required role.
#     """
#     collection_repository = Repository(session, cache, Collection)

#     collection = await collection_repository.select(id=schema.collection_id)
#     if not collection:
#         raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
#                 status_code=status.HTTP_404_NOT_FOUND)

#     collection_exists = await collection_repository.exists(
#         collection_name__eq=schema.collection_name, id__ne=collection.id)
#     if collection_exists:
#         raise E("collection_name", schema.collection_name, E.VALUE_DUPLICATED,
#                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

#     collection.is_locked = schema.is_locked
#     collection.collection_name = schema.collection_name
#     collection.collection_summary = schema.collection_summary
#     await collection_repository.update(collection, commit=False)

#     hook = Hook(session, cache, request, current_user=current_user)
#     await hook.execute(H.BEFORE_COLLECTION_UPDATE, collection)

#     await collection_repository.commit()
#     await hook.execute(H.AFTER_COLLECTION_UPDATE, collection)

#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"collection_id": collection.id}
#     )


# @router.delete("/collection/{collection_id}", name="Delete collection",
#                tags=["collections"], response_model=CollectionDeleteResponse)
# async def collection_delete(
#     request: Request,
#     session=Depends(get_session),
#     cache=Depends(get_cache),
#     current_user: User = Depends(auth(UserRole.admin)),
#     schema=Depends(CollectionDeleteRequest)
# ) -> dict:
#     """
#     Delete a collection entity by its ID. The router retrieves the
#     collection from the repository using the provided ID, verifies that
#     it exists, deletes the collection and all related entities, executes
#     related hooks, and returns the deleted collection ID in a JSON
#     response. The current user should have an admin role. Returns a 200
#     response on success, a 404 error if the collection is not found, and
#     a 403 error if authentication fails or the user does not have the
#     required role.
#     """
#     collection_repository = Repository(session, cache, Collection)

#     collection = await collection_repository.select(id=schema.collection_id)
#     if not collection:
#         raise E("collection_id", schema.collection_id, E.RESOURCE_NOT_FOUND,
#                 status_code=status.HTTP_404_NOT_FOUND)

#     await collection_repository.delete(collection, commit=False)

#     hook = Hook(session, cache, request, current_user=current_user)
#     await hook.execute(H.BEFORE_COLLECTION_DELETE, collection)

#     await collection_repository.commit()
#     await hook.execute(H.AFTER_COLLECTION_DELETE, collection)

#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"collection_id": collection.id}
#     )


# @router.get("/collections", name="Collections list",
#             tags=["collections"], response_model=CollectionsListResponse)
# async def collections_list(
#     request: Request,
#     session=Depends(get_session),
#     cache=Depends(get_cache),
#     current_user: User = Depends(auth(UserRole.reader)),
#     schema=Depends(CollectionsListRequest)
# ) -> dict:
#     """
#     Retrieve a list of collection entities based on the provided
#     parameters. The router fetches the list of collections from the
#     repository, executes related hooks, and returns the results in
#     a JSON response. The current user should have a reader role or
#     higher. Returns a 200 response on success and a 403 error if
#     authentication fails or the user does not have the required role.
#     """
#     collection_repository = Repository(session, cache, Collection)

#     collections = await collection_repository.select_all(**schema.__dict__)
#     collections_count = await collection_repository.count_all(
#         **schema.__dict__)

#     hook = Hook(session, cache, request, current_user=current_user)
#     await hook.execute(H.AFTER_COLLECTIONS_LIST, collections)

#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={
#             "collections": [collection.to_dict() for collection in collections],  # noqa E501
#             "collections_count": collections_count,
#         }
#     )
