from fastapi import APIRouter, status
import time
from fastapi.responses import JSONResponse
from app.schemas.time_schemas import TimeRetrieveResponse

router = APIRouter()


@router.get("/time", summary="Retrieve current time",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TimeRetrieveResponse, tags=["system"])
async def time_retrieve() -> TimeRetrieveResponse:
    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
    }
