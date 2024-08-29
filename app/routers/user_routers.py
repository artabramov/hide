"""
This module provides routers for managing users and authentication. It
includes functionality for registering new users, retrieving user
details by ID, updating user information (including role and password),
and handling userpics. Users must have appropriate roles, such as reader
or admin, to perform these actions. The routers support operations such
as creating users, updating roles and passwords, uploading and deleting
userpics, and listing users. The module also includes error handling for
invalid requests and insufficient permissions, with response codes
including 200 for success, 403 for forbidden actions due to role or
token issues, 404 for not found, and 422 for invalid data or query
parameters.
"""

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
    UserLoginResponse, TokenRetrieveRequest, TokenRetrieveResponse,
    TokenInvalidateRequest, TokenInvalidateResponse, UserSelectRequest,
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


@router.get("/auth/login", name="Authenticate user",
            tags=["auth"], response_model=UserLoginResponse)
async def user_login(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(UserLoginRequest)
) -> dict:
    """
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

    elif user.suspended_date > int(time()):
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
        user.logged_date = time()
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


@router.get("/auth/token", name="Retrieve token",
            tags=["auth"], response_model=TokenRetrieveResponse)
async def token_retrieve(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(TokenRetrieveRequest)
) -> dict:
    """
    Retrieves a token by validating the provided one-time password
    (TOTP). Requires the user to be active and have accepted the
    password. Returns a 200 response with the token upon success.
    Returns a 404 error if the user is not found, a 403 error if
    the user is inactive, and a 422 error if the TOTP is incorrect.
    Requires the user to have the reader role or higher.
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
                status_code=status.HTTP_403_FORBIDDEN)

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
        user_token = jwt_encode(user, token_exp=schema.token_exp)

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


@router.delete("/auth/token", name="Invalidate token",
               tags=["auth"], response_model=TokenInvalidateResponse)
async def token_invalidate(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(TokenInvalidateRequest)
) -> dict:
    """
    Invalidates the current user's token by updating their JTI. Requires
    the user to have the reader role or higher. Returns a 200 response
    with an empty dictionary upon successful invalidation. Returns a 403
    error if the user's token is invalid or if the user does not have
    the required role.
    """
    user_repository = Repository(session, cache, User)
    current_user.jti = jti_create()
    await user_repository.update(current_user)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_TOKEN_INVALIDATE, current_user)

    return {}


@router.post("/user", name="Register user",
             tags=["users"], response_model=UserRegisterResponse)
async def user_register(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(UserRegisterRequest)
) -> dict:
    """
    Registers a new user. Checks if the user login already exists and
    raises a 422 error if it does. If the login is unique, creates a new
    user with the provided details and returns a 201 response with the
    user's ID, MFA secret, and MFA URL. Requires the user to have the
    reader role or higher.
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
        schema.last_name, user_signature=schema.user_signature,
        user_contacts=schema.user_contacts)
    await user_repository.insert(user)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.AFTER_USER_REGISTER, user)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }


@router.get("/user/{user_id}", name="Retrieve user",
            tags=["users"], response_model=UserSelectResponse)
async def user_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(UserSelectRequest)
) -> dict:
    """
    Retrieves a user by their ID. Returns a 200 response with the user's
    details if found. Raises a 404 error if the user is not found.
    Requires the user to have the reader role or higher. Returns a 403
    error if the user's token is invalid or if the user does not have
    the required role.
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
    Updates the details of a user. Modifies the first name, last name,
    user signature, and user contacts for the specified user. Requires
    the user to have the reader role or higher. Returns a 200 response
    with the updated user's ID. Raises a 403 error if the user does not
    have the required role or if the user is attempting to update a
    different user's details.
    """
    if schema.user_id != current_user.id:
        raise E("user_id", schema.user_id, E.RESOURCE_FORBIDDEN,
                status_code=status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    current_user.first_name = schema.first_name
    current_user.last_name = schema.last_name
    current_user.user_signature = schema.user_signature
    current_user.user_contacts = schema.user_contacts
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
    Updates the role and active status of a user. Requires the current
    user to have an admin role. The user being updated must be different
    from the current user. Returns a 200 response with the ID of the
    updated user. Raises a 403 error if the current user tries to update
    their own role, if the user's token is invalid, or if the user does
    not have the required role. Returns a 404 error if the user to be
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
    Updates the password for a user. Requires the current user to have
    a reader role or higher. The user ID in the request must match the
    current user ID. Returns a 200 response with the ID of the updated
    user. Raises a 403 error if the user's token is invalid or if the
    user does not have the required role. Raises a 422 error if the
    current password is incorrect.
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
    Deletes the existing userpic if it exists, uploads and saves a new
    one, resizes it to the specified dimensions, and updates the user's
    data with the new userpic. Allowed for the current user only.
    Requires the user to have a reader role or higher. Returns a 200
    response with the user ID. Raises a 403 error if the user attempts
    to upload a userpic for a different user, or if the user's token is
    invalid. Raises a 422 error if the file's MIME type is unsupported.
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
    Deletes the userpic if it exists and updates the user's data to
    remove the userpic. Allowed for the current user only. Requires the
    user to have a reader role or higher. Returns a 200 response with
    the user ID. Raises a 403 error if the user attempts to delete a
    userpic for a different user or if the user's token is invalid.
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
    Retrieves a list of users and their count based on the provided
    query parameters. Requires the current user to have at least a
    reader role to access the user list. Returns a 200 response with
    the list of users and the total count. Raises a 403 error if the
    user's token is invalid or if the user does not have the required
    role. Raises a 422 error if any query parameters are invalid.
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
