"""
The module defines a FastAPI router for deleting user entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserDeleteResponse
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.delete("/user/{user_id}", summary="Delete a user",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserDeleteResponse, tags=["users"])
@locked
async def user_delete(
    user_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> UserDeleteResponse:
    """
    FastAPI router for deleting a user entity. The router checks if the
    current user  is not trying to delete their own account, retrieves
    the user from the repository using the provided ID, verifies if the
    user exists, deletes the user, and executes related hooks. The
    current user should have an admin role. Returns a 200 response on
    success, a 403 error if the current user attempts to delete their
    own account or if an exception occurs during deletion, and a 404
    error if the user is not found.
    """
    if user_id == current_user.id:
        raise E(["path", "user_id"], user_id,
                E.ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E(["path", "user_id"], user_id,
                E.ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    try:
        await user_repository.delete(user, commit=False)

    except Exception:
        raise E(["path", "user_id"], user_id,
                E.ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    hook = Hook(session, cache, current_user=current_user)
    await hook.execute(H.BEFORE_USER_DELETE, user)

    await user_repository.commit()
    await hook.execute(H.AFTER_USER_DELETE, user)

    return {"user_id": user.id}
