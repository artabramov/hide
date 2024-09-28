from fastapi import APIRouter, Depends, status
from app.decorators.locked_decorator import unlock
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.lock_schemas import LockDeleteResponse
from app.auth import auth
from app.hooks import Hook
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_LOCK_DELETE

router = APIRouter()


@router.delete("/lock", summary="Disable lockdown mode",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=LockDeleteResponse, tags=["system"])
async def lock_delete(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockDeleteResponse:
    await unlock()

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_LOCK_DELETE)

    return {"is_locked": False}
