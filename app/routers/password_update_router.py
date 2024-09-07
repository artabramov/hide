from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.helpers.hash_helper import get_hash
from app.schemas.user_schemas import (
    PasswordUpdateRequest, PasswordUpdateResponse)
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}/password", summary="Change user password",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PasswordUpdateResponse, tags=["users"])
async def password_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(PasswordUpdateRequest)
) -> PasswordUpdateResponse:
    """
    FastAPI router for updating a user password. Requires the current
    user to have a reader role or higher. The user ID in the request
    must match the current user ID. Returns a 200 response with the ID
    of the updated user. Raises a 403 error if the user's token is
    invalid or if the user does not have the required role. Raises
    a 422 error if the current password is incorrect.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    current_password = schema.current_password.get_secret_value()
    current_hash = get_hash(current_password)
    if current_hash != current_user.password_hash:
        raise E("current_password", current_password, E.VALUE_INVALID,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_repository = Repository(session, cache, User)
    current_user.user_password = schema.updated_password
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_PASSWORD_UPDATE, current_user)

    await user_repository.commit()
    await hook.execute(H.AFTER_PASSWORD_UPDATE, current_user)

    return {"user_id": current_user.id}
