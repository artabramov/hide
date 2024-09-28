from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.mediafile_model import Mediafile
from app.models.revision_model import Revision
from app.schemas.mediafile_schemas import (
    MediafileUpdateRequest, MediafileUpdateResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.libraries.tag_library import TagLibrary
from app.errors import E
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_MEDIAFILE_UPDATE, HOOK_AFTER_MEDIAFILE_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/mediafile/{mediafile_id}",
            summary="Update a mediafile data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=MediafileUpdateResponse, tags=["mediafiles"])
@locked
async def mediafile_update(
    mediafile_id: int, schema: MediafileUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> MediafileUpdateResponse:

    # Validate the mediafile.

    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)

    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif mediafile.is_locked:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
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

    # Update the data of the mediafile itself.

    mediafile.collection_id = schema.collection_id
    mediafile.mediafile_name = schema.mediafile_name
    mediafile.mediafile_summary = schema.mediafile_summary
    await mediafile_repository.update(mediafile, commit=False)

    # If a collection ID is received, then update
    # the collection's counters.

    if collection:
        await mediafile_repository.lock_all()

        collection.mediafiles_count = await mediafile_repository.count_all(
            collection_id__eq=collection.id)

        collection.revisions_count = await mediafile_repository.sum_all(
            "revisions_count", collection_id__eq=collection.id)

        collection.revisions_size = await mediafile_repository.sum_all(
            "revisions_size", collection_id__eq=collection.id)

        await collection_repository.update(collection, commit=False)

    # If the mediafile already has a related collection,
    # then update the collection's counters.

    if mediafile.mediafile_collection:
        await mediafile_repository.lock_all()

        mediafile.mediafile_collection.mediafiles_count = (
            await mediafile_repository.count_all(
                collection_id__eq=mediafile.mediafile_collection.id))

        mediafile.mediafile_collection.revisions_count = (
            await mediafile_repository.sum_all(
                "revisions_count",
                collection_id__eq=mediafile.mediafile_collection.id))

        mediafile.mediafile_collection.revisions_size = (
            await mediafile_repository.sum_all(
                "revisions_size",
                collection_id__eq=mediafile.mediafile_collection.id))

        await collection_repository.update(
            mediafile.mediafile_collection, commit=False)

    # Update the original filename for the latest revision
    # associated with the mediafile.

    if mediafile.latest_revision.original_filename != mediafile.mediafile_name:
        mediafile.latest_revision.original_filename = mediafile.mediafile_name

        revision_repository = Repository(session, cache, Revision)
        await revision_repository.update(
            mediafile.latest_revision, commit=False)

    # Update tags associated with the mediafile.

    tag_library = TagLibrary(session, cache)
    await tag_library.delete_all(mediafile.id, commit=False)

    tag_values = tag_library.extract_values(schema.tags)
    await tag_library.insert_all(mediafile.id, tag_values, commit=False)

    # Execute the corresponding hooks before and
    # after committing the changes

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_MEDIAFILE_UPDATE, mediafile)

    await mediafile_repository.commit()
    await hook.do(HOOK_AFTER_MEDIAFILE_UPDATE, mediafile)

    return {
        "mediafile_id": mediafile.id,
        "revision_id": mediafile.latest_revision.id,
    }
