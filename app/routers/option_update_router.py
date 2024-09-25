from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.option_model import Option
from app.schemas.option_schemas import (
    OptionUpdateRequest, OptionUpdateResponse)
from app.repository import Repository
from app.hooks import H, Hook
from app.errors import E
from app.auth import auth
from app.constants import LOC_PATH

router = APIRouter()


@router.put("/option/{option_key}", summary="Update an option",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=OptionUpdateResponse, tags=["options"])
@locked
async def option_delete(
    option_key: str, schema: OptionUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin)),
) -> OptionUpdateResponse:
    option_repository = Repository(session, cache, Option)
    option = await option_repository.select(option_key__eq=option_key)

    if not option:
        raise E([LOC_PATH, "option_key"], option_key,
                E.ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    option.option_value = schema.option_value
    await option_repository.update(option, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(H.BEFORE_OPTION_DELETE, option)

    await option_repository.commit()
    await hook.do(H.AFTER_OPTION_DELETE, option)

    return {"option_key": option.option_key if option else None}
