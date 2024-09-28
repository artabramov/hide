from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.mediafile_model import Mediafile
from app.models.revision_model import Revision
from app.models.download_model import Download
from app.hooks import Hook
from app.errors import E
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_REVISION_DOWNLOAD,
    HOOK_AFTER_REVISION_DOWNLOAD)

router = APIRouter()


@router.get("/mediafile/{mediafile_id}/download",
            summary="Download the latest revision of a mediafile.",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["mediafiles"])
@locked
async def mediafile_download(
    mediafile_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile = await mediafile_repository.select(id=mediafile_id)
    if not mediafile:
        raise E([LOC_PATH, "mediafile_id"], mediafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)
    mediafile.latest_revision = await revision_repository.select(
        id=mediafile.latest_revision_id)

    data = await FileManager.read(mediafile.latest_revision.revision_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(
        current_user.id, mediafile.id, mediafile.latest_revision.id)
    await download_repository.insert(download, commit=False)

    mediafile_repository = Repository(session, cache, Mediafile)
    mediafile.downloads_count = (
        await download_repository.count_all(mediafile_id__eq=mediafile.id))
    await mediafile_repository.update(mediafile, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_REVISION_DOWNLOAD, mediafile.latest_revision)

    await mediafile_repository.commit()
    await hook.do(HOOK_AFTER_REVISION_DOWNLOAD, mediafile.latest_revision)

    headers = {"Content-Disposition": f"attachment; filename={mediafile.latest_revision.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=mediafile.latest_revision.original_mimetype)
