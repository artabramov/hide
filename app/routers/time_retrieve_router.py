from fastapi import APIRouter, status, Depends
import time
from fastapi.responses import JSONResponse
from app.schemas.time_schemas import TimeRetrieveResponse
from app.hooks import Hook
from app.database import get_session
from app.cache import get_cache
from app.constants import HOOK_ON_TIME_RETRIEVE

router = APIRouter()


@router.get("/time", summary="Retrieve current time",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TimeRetrieveResponse, tags=["Services"])
async def time_retrieve(
    session=Depends(get_session), cache=Depends(get_cache)
) -> TimeRetrieveResponse:

    hook = Hook(session, cache)
    await hook.do(HOOK_ON_TIME_RETRIEVE)

    return {
        "unix_timestamp": int(time.time()),
        "timezone_name": time.tzname[0],
        "timezone_offset": time.timezone,
    }
