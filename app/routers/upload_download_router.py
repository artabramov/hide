"""
The module defines a FastAPI router for downloading revision entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.upload_model import Upload
from app.models.download_model import Download
from app.hooks import H, Hook
from app.errors import E
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager

router = APIRouter()


@router.get("/upload/{upload_id}/download", summary="Download uploaded file",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["uploads"])
@locked
async def upload_download(
    upload_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    """
    FastAPI router for downloading a revision entity. The router
    retrieves the specified revision from the repository, decrypts the
    associated file, executes related hooks, and returns the file as an
    attachment. The current user should have a reader role or higher.
    Returns a 200 response on success, a 404 error if the revision is
    not found, and a 403 error if authentication fails or the user
    does not have the required role.
    """
    upload_repository = Repository(session, cache, Upload)
    upload = await upload_repository.select(id=upload_id)
    if not upload:
        raise E([E.LOC_PATH, "upload_id"], upload_id,
                E.ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    data = await FileManager.read(upload.upload_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(current_user.id, upload.upload_document.id, upload.id)
    await download_repository.insert(download, commit=False)

    document_repository = Repository(session, cache, Document)
    upload.upload_document.downloads_count = (
        await download_repository.count_all(
            document_id__eq=upload.upload_document.id))
    await document_repository.update(upload.upload_document, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.BEFORE_UPLOAD_DOWNLOAD, upload)

    await upload_repository.commit()
    await hook.execute(H.AFTER_UPLOAD_DOWNLOAD, upload)

    headers = {"Content-Disposition": f"attachment; filename={upload.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=upload.original_mimetype)
