from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.helpers.jwt_helper import jti_create
from app.schemas.user_schemas import (
    TokenInvalidateRequest, TokenInvalidateResponse)
from app.hooks import H, Hook
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.delete("/auth/token", summary="Invalidate token",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=TokenInvalidateResponse, tags=["auth"])
async def token_invalidate(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(TokenInvalidateRequest)
) -> TokenInvalidateResponse:
    """
    FastAPI router for invalidating the current user's token by updating
    their JTI. Requires the user to have the reader role or higher.
    Returns a 200 response with an empty dictionary upon successful
    invalidation. Returns a 403 error if the user's token is invalid or
    if the user does not have the required role.
    """
    user_repository = Repository(session, cache, User)
    current_user.jti = jti_create()
    await user_repository.update(current_user, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_TOKEN_INVALIDATE, current_user)

    await user_repository.commit()
    await hook.execute(H.AFTER_TOKEN_INVALIDATE, current_user)

    return {}
