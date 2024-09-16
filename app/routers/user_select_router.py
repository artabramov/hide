from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserSelectRequest, UserSelectResponse
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get("/user/{user_id}", summary="Retrieve user",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserSelectResponse, tags=["users"])
@locked
async def user_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserSelectRequest)
) -> UserSelectResponse:
    """
    FastAPI router for retrieving a user entity. Returns a 200 response
    with the user's details if found. Raises a 404 error if the user is
    not found. Requires the user to have the reader role or higher.
    Returns a 403 error if the user's token is invalid or if the user
    does not have the required role.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=schema.user_id)

    if not user:
        raise E("user_id", schema.user_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.AFTER_USER_SELECT, user)

    return user.to_dict()
