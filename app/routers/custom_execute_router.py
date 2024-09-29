from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from app.schemas.custom_schemas import CustomExecuteRequest
from app.hooks import Hook
from app.database import get_session
from app.cache import get_cache
from app.auth import auth
from app.models.user_model import User, UserRole
from app.constants import HOOK_ON_CUSTOM_EXECUTE
from app.decorators.locked_decorator import locked

router = APIRouter()


@router.post("/custom", summary="Execute custom handler",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             tags=["Services"])
@locked
async def custom_execute(
    schema: CustomExecuteRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):

    response = {}

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_CUSTOM_EXECUTE, schema.params, response)

    return response
