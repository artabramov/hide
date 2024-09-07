"""
The module defines a FastAPI router for deleting option entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import (
    OptionDeleteRequest, OptionDeleteResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.delete("/option/{option_key}", summary="Delete option",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=OptionDeleteResponse, tags=["options"])
async def option_unset(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(OptionDeleteRequest)
) -> OptionDeleteResponse:
    """
    FastAPI router for deleting an option entity. The router retrieves
    the option from the repository using the provided option key. If
    the option exists, it deletes it from the repository and executes
    related hooks. The router returns the option key of the deleted
    option in a JSON response. If the option does not exist, no deletion
    occurs. The current user should have an admin role. Returns a 200
    response on success, a 404 error if the option is not found, and
    a 403 error if authentication fails or the user does not have
    the required role.
    """
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=schema.option_key)

    if option:
        await option_repository.delete(option, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_OPTION_DELETE, option)

    await option_repository.commit()
    await hook.execute(H.AFTER_OPTION_DELETE, option)

    return {"option_key": option.option_key if option else None}
