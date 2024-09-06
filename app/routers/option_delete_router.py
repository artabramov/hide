"""
The module defines a FastAPI router for deleting option entities by
their keys.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.option_models import Option
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
    FastAPI router for deleting an option entity by its key. Includes
    validation and execution of relevant hooks. Returns the key of the
    deleted option or None if the option was not found.
    """
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=schema.option_key)

    if option:
        await option_repository.delete(option, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_OPTION_DELETE, option)

    await option_repository.commit()
    await hook.execute(H.AFTER_OPTION_DELETE, option)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"option_key": option.option_key if option else None}
    )
