from fastapi import APIRouter, status
import time
from app.decorators.locked_decorator import is_locked
from fastapi.responses import JSONResponse
from app.schemas.service_schemas import HelloResponse

router = APIRouter()


@router.get("/service/hello", summary="Say hello",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=HelloResponse, tags=["services"])
async def service_hello():
    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
        "is_locked": is_locked(),
    }
