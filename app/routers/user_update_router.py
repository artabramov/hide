from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserUpdateRequest, UserUpdateResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    HOOK_BEFORE_USER_UPDATE, HOOK_AFTER_USER_UPDATE)

router = APIRouter()


@router.put("/user/{user_id}", summary="Update user",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserUpdateResponse, tags=["Users"])
@locked
async def user_update(
    user_id: int, schema: UserUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserUpdateResponse:
    """
    FastAPI router for updating a user entity. Modifies the first name,
    last name, user signature, and user contacts for the specified user.
    Requires the user to have the reader role or higher. Returns a 200
    response with the updated user's ID. Raises a 403 error if the user
    does not have the required role or if the user is attempting to
    update a different user's details.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    current_user.first_name = schema.first_name
    current_user.last_name = schema.last_name
    current_user.user_signature = schema.user_signature
    current_user.user_contacts = schema.user_contacts
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_USER_UPDATE, current_user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_USER_UPDATE, current_user)

    return {"user_id": current_user.id}
