"""
The module defines a FastAPI router for retrieving option entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import (
    OptionSelectRequest, OptionSelectResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/option/{option_key}", summary="Select option",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionSelectResponse, tags=["options"])
async def option_select(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(OptionSelectRequest)
) -> OptionSelectResponse:
    """
    FastAPI router for fetching an option entity. The router retrieves
    the option from the repository using the provided option key and
    executes related hooks. The current user should have an admin role.
    Returns a 200 response on success, a 404 error if the option is not
    found, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=schema.option_key)

    if not option:
        raise E("option_key", schema.option_key, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_OPTION_SELECT, option)

    return option.to_dict()
