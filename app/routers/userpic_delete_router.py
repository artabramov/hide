from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import (
    UserpicDeleteRequest, UserpicDeleteResponse)
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager

router = APIRouter()


@router.delete("/user/{user_id}/userpic", summary="Remove userpic",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserpicDeleteResponse, tags=["users"])
@locked
async def userpic_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserpicDeleteRequest)
) -> UserpicDeleteResponse:
    """
    FastAPI router for deleting a userpic. Deletes the userpic if it
    exists and updates the user's data to remove the userpic. Allowed
    for the current user only. Requires the user to have a reader role
    or higher. Returns a 200 response with the user ID. Raises a 403
    error if the user attempts to delete a userpic for a different user
    or if the user's token is invalid.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    if current_user.userpic_filename:
        await FileManager.delete(current_user.userpic_path)

    user_repository = Repository(session, cache, User)
    current_user.userpic_filename = None
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_USERPIC_DELETE, current_user)

    await user_repository.commit()
    await hook.execute(H.AFTER_USERPIC_DELETE, current_user)

    return {"user_id": current_user.id}
