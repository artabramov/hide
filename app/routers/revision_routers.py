from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.document_models import Document
from app.models.revision_models import Revision
from app.models.download_models import Download
from app.schemas.revision_schemas import RevisionDownloadRequest
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()
router = APIRouter()


@router.get("/revision/{revision_id}/download", tags=["revisions"],
            name="Download revision")
async def revision_download(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(RevisionDownloadRequest)
) -> Response:

    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=schema.revision_id)
    if not revision:
        raise HTTPException(status_code=404)

    data = await FileManager.read(revision.revision_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(current_user.id, revision.revision_document.id,
                        revision.id)
    await download_repository.insert(download)

    document_repository = Repository(session, cache, Document)
    revision.revision_document.downloads_count = await download_repository.count_all(  # noqa E501
        document_id__eq=revision.revision_document.id)
    await document_repository.update(revision.revision_document)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_DOCUMENT_DOWNLOAD, revision.revision_document)

    headers = {"Content-Disposition": f"attachment; filename={revision.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=revision.original_mimetype)
