import time
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.helpers.hash_helper import get_hash
from app.schemas.user_schemas import UserLoginRequest, UserLoginResponse
from app.errors import E
from app.hooks import H, Hook
from app.repository import Repository
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.get("/auth/login", summary="Authenticate user",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UserLoginResponse, tags=["auth"])
async def user_login(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(UserLoginRequest)
) -> UserLoginResponse:
    """
    FastAPI router for the first step of multi-factor authentication.
    Authenticates a user by validating their login credentials. Returns
    a 200 response with a confirmation of password acceptance upon
    successful authentication. Returns a 404 error if the user is not
    found, a 403 error if the user is suspended or inactive, and a 422
    error if the password is invalid. Invalid passwords increase the
    attempt count and may lead to user suspension if the attempt limit
    is exceeded.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise E("user_login", schema.user_login, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif user.suspended_date > int(time.time()):
        raise E("user_login", schema.user_login, E.USER_SUSPENDED,
                status_code=status.HTTP_403_FORBIDDEN)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.admin, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E("user_login", schema.user_login, E.USER_INACTIVE,
                status_code=status.HTTP_403_FORBIDDEN)

    user_password = schema.user_password.get_secret_value()
    password_hash = get_hash(user_password)

    if user.password_hash == password_hash:
        user.last_login_date = time.time()
        user.password_accepted = True
        user.password_attempts = 0

    else:
        user.password_accepted = False

        if user.password_attempts >= cfg.USER_LOGIN_ATTEMPTS - 1:
            user.suspended_date = int(time.time()) + cfg.USER_SUSPENDED_TIME
            user.password_attempts = 0

        else:
            user.suspended_date = 0
            user.password_attempts += 1

    await user_repository.update(user, commit=False)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.BEFORE_USER_LOGIN, user)

    await user_repository.commit()
    await hook.execute(H.AFTER_USER_LOGIN, user)

    if user.password_accepted:
        return {"password_accepted": True}

    else:
        raise E("user_password", schema.user_login, E.VALUE_INVALID,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
