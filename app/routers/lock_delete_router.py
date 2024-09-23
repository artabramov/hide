from fastapi import APIRouter, Depends, status
from app.decorators.locked_decorator import unlock
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.lock_schemas import LockDeleteResponse
from app.auth import auth

router = APIRouter()


@router.delete("/lock", summary="Unlock the app",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=LockDeleteResponse, tags=["system"])
async def lock_delete(
    current_user: User = Depends(auth(UserRole.admin))
) -> LockDeleteResponse:
    await unlock()
    return {"is_locked": False}
