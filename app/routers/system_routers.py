from fastapi import APIRouter, Depends
import time
from fastapi.security import HTTPBearer
from app.repositories.basic_repository import BasicRepository
from app.postgres import get_session
from app.redis import get_cache
from app.hooks import H

router = APIRouter()
jwt = HTTPBearer()


@router.get("/time", tags=["system"])
async def current_time():
    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
    }


@router.get("/execute", tags=["system"])
async def execute(session=Depends(get_session), cache=Depends(get_cache)):
    basic_repository = BasicRepository(session, cache)
    return await basic_repository.execute_hook(H.ON_EXECUTE)
