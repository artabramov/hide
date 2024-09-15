from fastapi import APIRouter, Depends, status
from app.decorators.locked_decorator import unlock
from fastapi.responses import JSONResponse
from app.models.user_model import User, UserRole
from app.schemas.service_schemas import UnlockResponse
from app.auth import auth

router = APIRouter()


@router.get("/unlock", summary="Unlock app",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=UnlockResponse, tags=["services"])
async def service_unlock(current_user: User = Depends(auth(UserRole.admin)),):
    await unlock()
    return {"is_locked": False}
