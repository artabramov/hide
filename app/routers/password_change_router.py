from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.helpers.hash_helper import get_hash
from app.schemas.user_schemas import (
    PasswordUpdateRequest, PasswordUpdateResponse)
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import (
    LOC_PATH, LOC_BODY, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    ERR_VALUE_INVALID, HOOK_BEFORE_PASSWORD_CHANGE, HOOK_AFTER_PASSWORD_CHANGE)

router = APIRouter()


@router.put("/user/{user_id}/password", summary="Change user password",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=PasswordUpdateResponse, tags=["users"])
@locked
async def password_change(
    user_id: int, schema: PasswordUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> PasswordUpdateResponse:
    """
    FastAPI router for updating a user password. Requires the current
    user to have a reader role or higher. The user ID in the request
    must match the current user ID. Returns a 200 response with the ID
    of the updated user. Raises a 403 error if the user's token is
    invalid or if the user does not have the required role. Raises
    a 422 error if the current password is incorrect.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    if get_hash(schema.current_password) != current_user.password_hash:
        raise E([LOC_BODY, "current_password"], schema.current_password,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_repository = Repository(session, cache, User)
    current_user.user_password = schema.updated_password
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_PASSWORD_CHANGE, current_user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_PASSWORD_CHANGE, current_user)

    return {"user_id": current_user.id}
