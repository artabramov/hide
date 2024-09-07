from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.schemas.user_schemas import UserUpdateRequest, UserUpdateResponse
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.put("/user/{user_id}", summary="Update user",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserUpdateResponse, tags=["users"])
async def user_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserUpdateRequest)
) -> UserUpdateResponse:
    """
    FastAPI router for updating a user entity. Modifies the first name,
    last name, user signature, and user contacts for the specified user.
    Requires the user to have the reader role or higher. Returns a 200
    response with the updated user's ID. Raises a 403 error if the user
    does not have the required role or if the user is attempting to
    update a different user's details.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    current_user.first_name = schema.first_name
    current_user.last_name = schema.last_name
    current_user.user_signature = schema.user_signature
    current_user.user_contacts = schema.user_contacts
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_USER_UPDATE, current_user)

    await user_repository.commit()
    await hook.execute(H.AFTER_USER_UPDATE, current_user)

    return {"user_id": current_user.id}
