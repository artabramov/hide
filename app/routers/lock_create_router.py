from fastapi import APIRouter, Depends, status
from app.decorators.locked_decorator import lock
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.lock_schemas import LockCreateResponse
from app.auth import auth
from app.hooks import H, Hook
from app.database import get_session
from app.cache import get_cache

router = APIRouter()


@router.post("/lock", summary="Lock the app",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=LockCreateResponse, tags=["system"])
async def lock_create(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockCreateResponse:
    await lock()

    hook = Hook(session, cache)
    await hook.execute(H.ON_LOCK_CREATE)

    return {"is_locked": True}