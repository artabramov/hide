from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.helpers.hash_helper import HashHelper
from app.helpers.jwt_helper import JWTHelper
from app.schemas.user_schemas import (
    UserRegisterRequest, UserRegisterResponse, UserLoginRequest,
    UserLoginResponse, TokenSelectRequest, TokenSelectResponse,
    TokenDeleteRequest, TokenDeleteResponse, UserSelectRequest,
    UserSelectResponse, UserpicUploadRequest)
from app.errors import E, Msg
from app.config import get_config
from time import time
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
import uuid
import os
from app.managers.file_manager import FileManager

router = APIRouter()
cfg = get_config()


@router.get("/user/login", response_model=UserLoginResponse, tags=["auth"],
            name="Authenticate a user")
async def user_login(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(UserLoginRequest)
) -> dict:
    """
    Authenticate a user by validating their login credentials. If
    the user is not found, suspended, or inactive, raises appropriate
    errors. On successful authentication, updates the user's password
    status and attempts, returning a confirmation of password
    acceptance. Invalid passwords increase the attempt count and may
    suspend the user if the limit is exceeded. Requires READER role
    or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    elif user.suspended_date > int(time()):
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_SUSPENDED)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.ADMIN, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_INACTIVE)

    user_password = schema.user_password.get_secret_value()
    password_hash = HashHelper.hash(user_password)

    if user.password_hash == password_hash:
        user.password_accepted = True
        user.password_attempts = 0

        await user_repository.update(user)

        hook = Hook(session, cache, request, current_user=user)
        await hook.execute(H.AFTER_USER_LOGIN, user)

        return {"password_accepted": True}

    else:
        user.password_accepted = False

        if user.password_attempts >= cfg.USER_LOGIN_ATTEMPTS - 1:
            user.suspended_date = int(time.time()) + cfg.USER_SUSPENDED_TIME
            user.password_attempts = 0

        else:
            user.suspended_date = 0
            user.password_attempts += 1

        await user_repository.update(user)
        raise E("user_password", user_password, Msg.USER_PASSWORD_INVALID)


@router.get("/auth/token", response_model=TokenSelectResponse, tags=["auth"],
            name="Retrieve a token")
async def token_retrieve(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(TokenSelectRequest)
) -> dict:
    """
    Retrieve a token by validating the provided one-time password.
    Checks if the user is active and has accepted the password. If the
    TOTP is correct, updates the user's status and role if needed, and
    returns a token. Raises errors if the user is not found, inactive,
    or the TOTP is incorrect. Requires READER role or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.ADMIN, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_INACTIVE)

    elif not user.password_accepted:
        raise E("user_login", schema.user_login, Msg.USER_PASSWORD_UNACCEPTED)

    user_totp = user.get_totp(user.mfa_secret)
    if user_totp == schema.user_totp:
        user.mfa_attempts = 0
        user.password_accepted = False

        if not admin_exists:
            user.is_active = True
            user.user_role = UserRole.ADMIN

        await user_repository.update(user)
        user_token = JWTHelper.encode_token(user)

        hook = Hook(session, cache, request, current_user=user)
        await hook.execute(H.AFTER_TOKEN_RETRIEVE, user)

        return {"user_token": user_token}

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= cfg.USER_MFA_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

        await user_repository.update(user)
        raise E("user_totp", schema.user_totp, Msg.USER_TOTP_INVALID)


@router.delete("/auth/token", response_model=TokenDeleteResponse,
               tags=["auth"], name="Invalidate the token")
async def token_invalidate(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.READER)),
    schema=Depends(TokenDeleteRequest)
) -> dict:
    """
    Invalidate the current user's token by updating their JTI. This
    action is only allowed for users with the READER role or higher.
    Returns an empty dictionary upon successful invalidation.
    """
    user_repository = Repository(session, cache, User)
    current_user.jti = JWTHelper.create_jti()
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_TOKEN_INVALIDATE, current_user)

    return {}


@router.post("/user", response_model=UserRegisterResponse, tags=["users"],
             name="Register a user")
async def user_register(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(UserRegisterRequest)
) -> dict:
    """
    Register a new user. Checks if the user login already exists and
    raises an error if it does. If the login is unique, creates a new
    user with the provided details. Returns the user's ID, MFA secret,
    and MFA URL. The action requires the user to have the READER role
    or higher.
    """
    user_repository = Repository(session, cache, User)
    user_exists = await user_repository.exists(
        user_login__eq=schema.user_login)

    if user_exists:
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_EXISTS)

    user_password = schema.user_password.get_secret_value()
    user = User(
        UserRole.READER, schema.user_login, user_password, schema.first_name,
        schema.last_name, user_summary=schema.user_summary)
    await user_repository.insert(user)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.AFTER_USER_REGISTER, user)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }


@router.get("/user/{user_id}", response_model=UserSelectResponse,
            tags=["users"], name="Retrieve a user")
async def user_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.READER)),
    schema=Depends(UserSelectRequest)
) -> dict:
    """
    Retrieve a user by their ID. If the user is found, return their
    details. If not found, raise a 404 error. Requires the user to
    have the READER role or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=schema.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.AFTER_USER_SELECT, user)

    return {
        "user": user.to_dict(),
    }


@router.post("/user/{user_id}/userpic", tags=["users"],
             name="Upload userpic")
async def userpic_upload(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.READER)),
    schema=Depends(UserpicUploadRequest)
) -> dict:
    userpic_filename = str(uuid.uuid4()) + cfg.USERPIC_EXTENSION
    userpic_path = os.path.join(cfg.USERPIC_PATH, userpic_filename)
    await FileManager.upload(schema.file, userpic_path)
    return {}
