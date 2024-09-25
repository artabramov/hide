from fastapi import APIRouter, status, Depends
from app.decorators.locked_decorator import is_locked, get_lock_time
from fastapi.responses import JSONResponse
from app.schemas.lock_schemas import LockRetrieveResponse
from app.models.user_model import User, UserRole
from app.auth import auth
from app.config import get_config
from app.hooks import H, Hook
from app.database import get_session
from app.cache import get_cache

cfg = get_config()
router = APIRouter()


@router.get("/lock", summary="Get the lock state",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockRetrieveResponse, tags=["system"])
async def lock_retrieve(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockRetrieveResponse:

    hook = Hook(session, cache)
    await hook.do(H.ON_LOCK_RETRIEVE)

    return {
        "is_locked": is_locked(),
        "lock_time": get_lock_time(),
    }
