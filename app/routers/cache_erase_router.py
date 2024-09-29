from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.auth import auth
from app.models.user_model import User, UserRole
from app.decorators.locked_decorator import locked
from app.managers.cache_manager import CacheManager
from app.hooks import Hook
from app.constants import HOOK_ON_CACHE_ERASE

router = APIRouter()


@router.delete("/cache", summary="Erase the cache",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               tags=["Services"])
@locked
async def cache_erase(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):
    cache_manager = CacheManager(cache)
    await cache_manager.erase()

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_ON_CACHE_ERASE)

    return {}
