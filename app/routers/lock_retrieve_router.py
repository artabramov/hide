from fastapi import APIRouter, status, Depends
import time
import os
from app.decorators.locked_decorator import lock_exists
from fastapi.responses import JSONResponse
from app.schemas.lock_schemas import LockRetrieveResponse
from app.database import get_session
from app.models.user_model import User, UserRole
from app.auth import auth
from app.config import get_config

cfg = get_config()
router = APIRouter()


@router.get("/lock", summary="Get the lock state",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockRetrieveResponse, tags=["system"])
async def lock_retrieve(
    session=Depends(get_session),
    current_user: User = Depends(auth(UserRole.admin))
) -> LockRetrieveResponse:
    is_locked = lock_exists()
    locked_time = 0
    if is_locked:
        lock_created = os.path.getctime(cfg.LOCK_FILE_PATH)
        locked_time = int(time.time() - lock_created)

    return {
        "is_locked": is_locked,
        "locked_time": locked_time,
    }
