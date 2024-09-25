from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.upload_model import Upload
from app.schemas.upload_schemas import UploadSelectResponse
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import LOC_PATH

router = APIRouter()


@router.get("/upload/{upload_id}", summary="Retrieve an upload",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UploadSelectResponse, tags=["uploads"])
@locked
async def upload_select(
    upload_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UploadSelectResponse:
    """
    FastAPI router for retrieving a revision entity. The router fetches
    the revision from the repository using the provided ID, executes
    related hooks, and returns the revision details in a JSON response.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the revision is not found, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    upload_repository = Repository(session, cache, Upload)
    upload = await upload_repository.select(id=upload_id)

    if not upload:
        raise E([LOC_PATH, "upload_id"], upload_id,
                E.ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(H.AFTER_UPLOAD_SELECT, upload)

    return upload.to_dict()
