from fastapi import APIRouter, Depends, HTTPException, status
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_models import User, UserRole
from app.helpers.hash_helper import HashHelper
from app.helpers.jwt_helper import JWTHelper
from app.schemas.user_schemas import (
    UserRegisterRequest, UserRegisterResponse, UserLoginRequest,
    UserLoginResponse, TokenSelectRequest, TokenSelectResponse,
    TokenDeleteRequest, TokenDeleteResponse,
    UserSelectRequest, UserSelectResponse)
from app.repositories.user_repository import UserRepository
from app.errors import E, Msg
from app.config import get_config
from time import time
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.get("/user/login", response_model=UserLoginResponse, tags=["auth"])
async def user_login(session=Depends(get_session), cache=Depends(get_cache),
                     schema=Depends(UserLoginRequest)):

    user_repository = UserRepository(session, cache)
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

    if user.password_hash != password_hash:
        user.password_accepted = False

        if user.password_attempts >= cfg.USER_LOGIN_ATTEMPTS - 1:
            user.suspended_date = int(time.time()) + cfg.USER_SUSPENDED_TIME
            user.password_attempts = 0

        else:
            user.suspended_date = 0
            user.password_attempts += 1

        await user_repository.update(user)
        raise E("user_password", user_password, Msg.USER_PASSWORD_INVALID)

    else:
        user.password_accepted = True
        user.password_attempts = 0

        await user_repository.update(user)
        return {"password_accepted": True}


@router.get("/auth/token", response_model=TokenSelectResponse, tags=["auth"])
async def token_select(session=Depends(get_session), cache=Depends(get_cache),
                       schema=Depends(TokenSelectRequest)):
    """Second step of authentication: sign in by user login and totp."""
    user_repository = UserRepository(session, cache)
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
        return {"user_token": user_token}

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= cfg.USER_MFA_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

        await user_repository.update(user)
        raise E("user_totp", schema.user_totp, Msg.USER_TOTP_INVALID)


@router.delete("/auth/token", response_model=TokenDeleteResponse, tags=["auth"])
async def token_delete(session=Depends(get_session), cache=Depends(get_cache),
                       current_user: User = Depends(auth(UserRole.READER)),
                       schema=Depends(TokenDeleteRequest)):
    """Logout: generate new jti."""
    user_repository = UserRepository(session, cache)
    current_user.jti = JWTHelper.create_jti()
    await user_repository.update(current_user)
    return {}


@router.post("/user", response_model=UserRegisterResponse, tags=["users"])
async def user_register(session=Depends(get_session), cache=Depends(get_cache),
                        schema=Depends(UserRegisterRequest)):

    user_repository = UserRepository(session, cache)
    user_exists = await user_repository.exists(user_login__eq=schema.user_login)

    if user_exists:
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_EXISTS)

    user_password = schema.user_password.get_secret_value()
    user_jti = JWTHelper.create_jti()
    user = User(UserRole.READER, schema.user_login, user_password,
                schema.first_name, schema.last_name, user_jti)

    hook = Hook(user_repository.entity_manager, user_repository.cache_manager)
    user = await hook.execute(H.BEFORE_USER_REGISTER, entity=user)
    user = await user_repository.insert(user)
    user = await hook.execute(H.AFTER_USER_REGISTER, entity=user)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }


@router.get("/user/{user_id}", response_model=UserSelectResponse, tags=["users"])  # noqa E501
async def user_select(session=Depends(get_session), cache=Depends(get_cache),
                      current_user: User = Depends(auth(UserRole.READER)),
                      schema=Depends(UserSelectRequest)):
    """Select user."""
    user_repository = UserRepository(session, cache)
    user = await user_repository.select(schema.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {
        "user": user.to_dict(),
    }
