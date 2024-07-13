from fastapi import APIRouter, Depends, HTTPException, status
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_models import User, UserRole
from app.helpers.hash_helper import HashHelper
from app.schemas.user_schemas import (
    UserRegisterRequest, UserRegisterResponse, UserLoginRequest,
    UserLoginResponse)
from app.repositories.user_repository import UserRepository
from app.errors import E, Msg
from app.config import get_config
from time import time

router = APIRouter()
cfg = get_config()


@router.post("/user", response_model=UserRegisterResponse, tags=["users"])
async def user_register(session=Depends(get_session), cache=Depends(get_cache),
                        schema=Depends(UserRegisterRequest)):

    user_repository = UserRepository(session, cache)
    user_exists = await user_repository.exists(user_login__eq=schema.user_login)

    if user_exists:
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_EXISTS)

    user_password = schema.user_password.get_secret_value()
    user = User(UserRole.READER, schema.user_login, user_password,
                first_name=schema.first_name, last_name=schema.last_name)

    user = await user_repository.insert(user)
    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }


@router.get("/user/login", response_model=UserLoginResponse, tags=["users"])
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
            user.password_attempts = user.password_attempts + 1

    else:
        user.password_accepted = True
        user.password_attempts = 0

    await user_repository.update(user)

    if not user.password_accepted:
        raise E("user_password", user_password, Msg.USER_PASSWORD_INVALID)

    return {
        "password_accepted": True,
    }
