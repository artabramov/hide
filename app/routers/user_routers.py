import uuid
import os
from time import time
from fastapi import APIRouter, Depends, status, Request
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.helpers.hash_helper import get_hash
from app.helpers.jwt_helper import jwt_encode, jti_create
from app.schemas.user_schemas import (
    UserRegisterRequest, UserRegisterResponse, UserLoginRequest,
    UserLoginResponse, TokenSelectRequest, TokenSelectResponse,
    TokenDeleteRequest, TokenDeleteResponse, UserSelectRequest,
    UserSelectResponse, UserpicUploadRequest, UserpicUploadResponse,
    UserpicDeleteRequest, UserpicDeleteResponse, UserUpdateRequest,
    UserUpdateResponse, RoleUpdateRequest, RoleUpdateResponse,
    PasswordUpdateRequest, PasswordUpdateResponse, UsersListRequest,
    UsersListResponse)
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.helpers.image_helper import image_resize
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.post("/user", name="Register a user",
             tags=["auth"], response_model=UserRegisterResponse)
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
    and MFA URL. The action requires the user to have the reader role
    or higher.
    """
    user_repository = Repository(session, cache, User)
    user_exists = await user_repository.exists(
        user_login__eq=schema.user_login)

    if user_exists:
        raise E("user_login", schema.user_login, E.VALUE_DUPLICATED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_password = schema.user_password.get_secret_value()
    user = User(
        UserRole.reader, schema.user_login, user_password, schema.first_name,
        schema.last_name, user_summary=schema.user_summary)
    await user_repository.insert(user)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.AFTER_USER_REGISTER, user)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }


@router.get("/user/login", name="Authenticate a user",
            tags=["auth"], response_model=UserLoginResponse)
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
    suspend the user if the limit is exceeded. Requires reader role
    or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise E("user_login", schema.user_login, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    elif user.suspended_date > int(time()):
        raise E("user_login", schema.user_login, E.USER_SUSPENDED,
                status_code=status.HTTP_401_UNAUTHORIZED)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.admin, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E("user_login", schema.user_login, E.USER_INACTIVE,
                status_code=status.HTTP_401_UNAUTHORIZED)

    user_password = schema.user_password.get_secret_value()
    password_hash = get_hash(user_password)

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

        raise E("user_password", schema.user_login, E.VALUE_INVALID,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@router.get("/auth/token", name="Retrieve a token",
            tags=["auth"], response_model=TokenSelectResponse)
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
    or the TOTP is incorrect. Requires reader role or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise E("user_login", schema.user_login, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.admin, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E("user_login", schema.user_login, E.USER_INACTIVE,
                status_code=status.HTTP_401_UNAUTHORIZED)

    elif not user.password_accepted:
        raise E("user_totp", schema.user_totp, E.VALUE_INVALID,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_totp = user.get_totp(user.mfa_secret)
    if user_totp == schema.user_totp:
        user.mfa_attempts = 0
        user.password_accepted = False

        if not admin_exists:
            user.is_active = True
            user.user_role = UserRole.admin

        await user_repository.update(user)
        user_token = jwt_encode(user)

        hook = Hook(session, cache, request, current_user=user)
        await hook.execute(H.AFTER_TOKEN_RETRIEVE, user)

        return {"user_token": user_token}

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= cfg.USER_MFA_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

        await user_repository.update(user)
        raise E("user_totp", schema.user_totp, E.VALUE_INVALID,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@router.delete("/auth/token", name="Invalidate the token",
               tags=["auth"], response_model=TokenDeleteResponse)
async def token_invalidate(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(TokenDeleteRequest)
) -> dict:
    """
    Invalidate the current user's token by updating their JTI. This
    action is only allowed for users with the reader role or higher.
    Returns an empty dictionary upon successful invalidation.
    """
    user_repository = Repository(session, cache, User)
    current_user.jti = jti_create()
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_TOKEN_INVALIDATE, current_user)

    return {}


@router.get("/user/{user_id}", name="Retrieve a user",
            tags=["users"], response_model=UserSelectResponse)
async def user_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserSelectRequest)
) -> dict:
    """
    Retrieve a user by their ID. If the user is found, return their
    details. If not found, raise a 404 error. Requires the user to
    have the reader role or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=schema.user_id)

    if not user:
        raise E("user_id", schema.user_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.AFTER_USER_SELECT, user)

    return user.to_dict()


@router.put("/user/{user_id}", name="Update a user",
            tags=["users"], response_model=UserUpdateResponse)
async def user_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserUpdateRequest)
) -> dict:
    """
    Update the user's details. Modify the first name, last name, and
    user summary for the current user. Requires user to have reader role
    or higher.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    current_user.first_name = schema.first_name
    current_user.last_name = schema.last_name
    current_user.user_summary = schema.user_summary
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_USER_UPDATE, current_user)

    return {
        "user_id": current_user.id,
    }


@router.put("/user/{user_id}/role", name="Update a user role",
            tags=["users"], response_model=RoleUpdateResponse)
async def role_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(RoleUpdateRequest)
) -> dict:
    """
    Update the role and active status of a user. Requires the current
    user to have an admin role. The user to be updated must be different
    from the current user. Returns the user ID of the updated user.
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
    await user_repository.update(user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_ROLE_UPDATE, user)

    return {
        "user_id": user.id,
    }


@router.put("/user/{user_id}/password", name="Update a user password",
            tags=["users"], response_model=PasswordUpdateResponse)
async def password_update(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(PasswordUpdateRequest)
) -> dict:
    """
    Update the password for a user. Requires the current user to have
    a reader role or higher. The user ID in the request must match
    the current user ID. Returns the user ID of the updated user.
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
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_PASSWORD_UPDATE, current_user)

    return {
        "user_id": current_user.id,
    }


@router.post("/user/{user_id}/userpic", name="Upload userpic",
             tags=["users"], response_model=UserpicUploadResponse)
async def userpic_upload(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserpicUploadRequest)
) -> dict:
    """
    Delete the existing userpic if exists. Upload and save the new one,
    resize it to the specified dimensions, and update the user's data
    with the new userpic. Allowed for current user only. Requires user
    to have reader role or higher.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    elif schema.file.content_type not in cfg.USERPIC_MIMES:
        raise E("user_id", schema.user_id, E.MIMETYPE_UNSUPPORTED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if current_user.userpic_filename:
        await FileManager.delete(current_user.userpic_path)

    userpic_filename = str(uuid.uuid4()) + cfg.USERPIC_EXTENSION
    userpic_path = os.path.join(cfg.USERPIC_BASE_PATH, userpic_filename)
    await FileManager.upload(schema.file, userpic_path)

    await image_resize(userpic_path, cfg.USERPIC_WIDTH,
                       cfg.USERPIC_HEIGHT, cfg.USERPIC_QUALITY)

    user_repository = Repository(session, cache, User)
    current_user.userpic_filename = userpic_filename
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_USERPIC_UPLOAD, current_user)

    return {
        "user_id": current_user.id
    }


@router.delete("/user/{user_id}/userpic", name="Delete userpic",
               tags=["users"], response_model=UserpicDeleteResponse)
async def userpic_delete(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserpicDeleteRequest)
) -> dict:
    """
    Delete the userpic if exists. Update the user's data to remove the
    userpic. Allowed for current user only. Requires user to have
    reader role or higher.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    if current_user.userpic_filename:
        await FileManager.delete(current_user.userpic_path)

    user_repository = Repository(session, cache, User)
    current_user.userpic_filename = None
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_USERPIC_DELETE, current_user)

    return {
        "user_id": current_user.id
    }


@router.get("/users", name="Retrieve users list",
            tags=["users"], response_model=UsersListResponse)
async def users_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UsersListRequest)
) -> dict:
    """
    Retrieve a list of users and their count based on the provided query
    parameters. Ensure that the current user has at least reader role
    to access the user list.
    """
    user_repository = Repository(session, cache, User)

    users = await user_repository.select_all(**schema.__dict__)
    users_count = await user_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_USERS_LIST, users)

    return {
        "users": [user.to_dict() for user in users],
        "users_count": users_count,
    }
