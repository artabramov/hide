from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import RoleUpdateRequest, RoleUpdateResponse
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}/role", summary="Change user role",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=RoleUpdateResponse, tags=["users"])
async def role_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(RoleUpdateRequest)
) -> RoleUpdateResponse:
    """
    FastAPI router for updating a user role. Requires the current user
    to have an admin role. The user being updated must be different from
    the current user. Returns a 200 response with the ID of the updated
    user. Raises a 403 error if the current user tries to update their
    own role, if the user's token is invalid, or if the user does not
    have the required role. Returns a 404 error if the user to be
    updated is not found.
    """
    if schema.user_id == current_user.id:
        raise E("user_id", schema.user_id, E.ENTITY_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=schema.user_id)

    if not user:
        raise E("user_id", schema.user_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    user.is_active = schema.is_active
    user.user_role = schema.user_role
    await user_repository.update(user, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_ROLE_UPDATE, user)

    await user_repository.commit()
    await hook.execute(H.AFTER_ROLE_UPDATE, user)

    return {"user_id": user.id}
