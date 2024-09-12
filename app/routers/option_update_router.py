"""
The module defines a FastAPI router for creating or updating option
entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import (
    OptionUpdateRequest, OptionUpdateResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.put("/option/{option_key}", summary="Set option",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionUpdateResponse, tags=["options"])
async def option_set(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(OptionUpdateRequest)
) -> OptionUpdateResponse:
    """
    FastAPI router for inserting or updating an option value. The router
    fetches the option from the repository using the provided option key,
    and if the option does not exist, creates a new one with the
    specified value. If the option does exist, it updates its value.
    The router then executes related hooks and returns the updated
    option key in a JSON response. The current user should have an admin
    role. Returns a 200 response on success, a 400 error if the request
    data is invalid, and a 403 error if authentication fails or the user
    does not have the required role.
    """
    option_repository = Repository(session, cache, Option)

    option = await option_repository.select(option_key__eq=schema.option_key)
    if not option:
        option = Option(
            current_user.id, schema.option_key, schema.option_value)
    else:
        option.option_value = schema.option_value

    await option_repository.update(option, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_OPTION_UPDATE, option)

    await option_repository.commit()
    await hook.execute(H.AFTER_OPTION_UPDATE, option)

    return {"option_key": option.option_key}
