from fastapi import APIRouter, status, Depends
from app.helpers.lock_helper import is_locked, get_lock_time
from fastapi.responses import JSONResponse
from app.schemas.lock_schemas import LockRetrieveResponse
from app.models.user_model import User, UserRole
from app.auth import auth
from app.config import get_config
from app.hooks import Hook
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_LOCK_RETRIEVE

cfg = get_config()
router = APIRouter()


@router.get("/lock", summary="Retrieve lockdown status",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockRetrieveResponse, tags=["services"])
async def lock_retrieve(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockRetrieveResponse:

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_LOCK_RETRIEVE)

    return {
        "is_locked": is_locked(),
        "lock_time": get_lock_time(),
    }
