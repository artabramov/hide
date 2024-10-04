from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.datafile_model import Datafile
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


@router.get("/datafile/{datafile_id}/download",
            summary="Download the latest revision of a datafile.",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["Datafiles"])
@locked
async def datafile_download(
    datafile_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    datafile_repository = Repository(session, cache, Datafile)
    datafile = await datafile_repository.select(id=datafile_id)
    if not datafile:
        raise E([LOC_PATH, "datafile_id"], datafile_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)
    datafile.latest_revision = await revision_repository.select(
        id=datafile.latest_revision_id)

    data = await FileManager.read(datafile.latest_revision.revision_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(
        current_user.id, datafile.id, datafile.latest_revision.id)
    await download_repository.insert(download, commit=False)

    datafile_repository = Repository(session, cache, Datafile)
    datafile.downloads_count = (
        await download_repository.count_all(datafile_id__eq=datafile.id))
    await datafile_repository.update(datafile, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_REVISION_DOWNLOAD, datafile.latest_revision)

    await datafile_repository.commit()
    await hook.do(HOOK_AFTER_REVISION_DOWNLOAD, datafile.latest_revision)

    headers = {"Content-Disposition": f"attachment; filename={datafile.latest_revision.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=datafile.latest_revision.original_mimetype)
