from fastapi import APIRouter, Depends, status
from app.decorators.locked_decorator import lock
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.system_schemas import SystemLockResponse
from app.auth import auth

router = APIRouter()


@router.post("/lock", summary="Lock the app",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             response_model=SystemLockResponse, tags=["system"])
async def lock_create(current_user: User = Depends(auth(UserRole.admin)),):
    await lock()
    return {"is_locked": True}
