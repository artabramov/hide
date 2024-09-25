from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from app.schemas.custom_schemas import CustomExecuteRequest
from app.hooks import H, Hook
from app.database import get_session
from app.cache import get_cache
from app.auth import auth
from app.models.user_model import User, UserRole

router = APIRouter()


@router.post("/execute", summary="Execute custom command",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             tags=["system"])
async def custom_execute(
    schema: CustomExecuteRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):

    response = {}

    hook = Hook(session, cache)
    await hook.do(H.ON_CUSTOM_EXECUTE, schema.params, response)

    return response
