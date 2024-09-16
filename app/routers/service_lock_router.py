from fastapi import APIRouter, Depends, status
from app.decorators.locked_decorator import lock
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.service_schemas import LockResponse
from app.auth import auth

router = APIRouter()


@router.get("/service/lock", summary="Lock app",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=LockResponse, tags=["services"])
async def service_lock(current_user: User = Depends(auth(UserRole.admin)),):
    await lock()
    return {"is_locked": True}
