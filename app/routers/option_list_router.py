"""
The module defines a FastAPI router for retrieving the option list with
pagination and sorting.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_models import User, UserRole
from app.models.option_models import Option
from app.schemas.option_schemas import (
    OptionsListRequest, OptionsListResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.get("/options", summary="Fetch option list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionsListResponse, tags=["options"])
async def options_list(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
    schema=Depends(OptionsListRequest)
) -> OptionsListResponse:
    """
    FastAPI router for retrieving a list of option entities with
    pagination and sorting. Includes validation and execution of
    relevant hooks. Returns the list of options and the total count
    of options.
    """
    option_repository = Repository(session, cache, Option)

    options = await option_repository.select_all(**schema.__dict__)
    options_count = await option_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.AFTER_OPTION_LIST, options)

    return {
        "options": [option.to_dict() for option in options],
        "options_count": options_count,
    }
