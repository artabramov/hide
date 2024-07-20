from fastapi import APIRouter
import time
from fastapi.security import HTTPBearer

router = APIRouter()
jwt = HTTPBearer()


@router.get("/time", tags=["system"])
async def current_time():
    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
    }
