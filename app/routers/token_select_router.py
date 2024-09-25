from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.helpers.jwt_helper import jwt_encode
from app.schemas.user_schemas import (
    TokenRetrieveRequest, TokenRetrieveResponse)
from app.errors import E
from app.hooks import H, Hook
from app.repository import Repository
from app.config import get_config
from app.constants import LOC_QUERY

router = APIRouter()
cfg = get_config()


@router.get("/auth/token", summary="Retrieve token",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TokenRetrieveResponse, tags=["auth"])
@locked
async def token_retrieve(
    schema=Depends(TokenRetrieveRequest),
    session=Depends(get_session), cache=Depends(get_cache)
) -> TokenRetrieveResponse:
    """
    FastAPI router for the second step of multi-factor authentication.
    Retrieves a JWT token by validating the provided one-time password
    (TOTP). Requires the user to be active and have accepted the
    password in the previous step. Returns a 200 response with the
    token upon success. Returns a 404 error if the user is not found,
    a 403 error if the user is inactive, and a 422 error if the TOTP is
    incorrect. Requires the user to have the reader role or higher.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(user_login__eq=schema.user_login)

    if not user:
        raise E([LOC_QUERY, "user_login"], schema.user_login,
                E.ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    admin_exists = await user_repository.exists(
        user_role__eq=UserRole.admin, is_active__eq=True)

    if not user.is_active and admin_exists:
        raise E([LOC_QUERY, "user_login"], schema.user_login,
                E.ERR_USER_INACTIVE, status.HTTP_403_FORBIDDEN)

    elif not user.password_accepted:
        raise E([LOC_QUERY, "user_totp"], schema.user_totp,
                E.ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    totp_accepted = schema.user_totp == user.get_totp(user.mfa_secret)

    if totp_accepted:
        user.mfa_attempts = 0
        user.password_accepted = False

        if not admin_exists:
            user.is_active = True
            user.user_role = UserRole.admin

    else:
        user.mfa_attempts += 1

        if user.mfa_attempts >= cfg.USER_MFA_ATTEMPTS:
            user.mfa_attempts = 0
            user.password_accepted = False

    await user_repository.update(user, commit=False)
    user_token = jwt_encode(user, token_exp=schema.token_exp)

    hook = Hook(session, cache)
    await hook.do(H.BEFORE_TOKEN_SELECT, user)

    await user_repository.commit()
    await hook.do(H.AFTER_TOKEN_SELECT, user)

    if totp_accepted:
        return {"user_token": user_token}

    else:
        raise E([LOC_QUERY, "user_totp"], schema.user_totp,
                E.ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)
