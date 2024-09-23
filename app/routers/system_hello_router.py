from fastapi import APIRouter, status
import time
from app.decorators.locked_decorator import is_locked
from fastapi.responses import JSONResponse
from app.schemas.system_schemas import SystemHelloResponse

router = APIRouter()


@router.get("/hello", summary="Hello!",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=SystemHelloResponse, tags=["system"])
async def hello_select():
    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
        "is_locked": is_locked(),
    }
