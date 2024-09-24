from fastapi import APIRouter, status, Depends
import time
from fastapi.responses import JSONResponse
from app.schemas.time_schemas import TimeRetrieveResponse
from app.hooks import H, Hook
from app.database import get_session
from app.cache import get_cache

router = APIRouter()


@router.get("/time", summary="Retrieve time",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TimeRetrieveResponse, tags=["system"])
async def time_retrieve(
    session=Depends(get_session), cache=Depends(get_cache)
) -> TimeRetrieveResponse:
    response = {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
    }

    hook = Hook(session, cache)
    await hook.execute(H.ON_TIME_RETRIEVE, response)

    return response
