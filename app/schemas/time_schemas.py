
from pydantic import BaseModel


class TimeRetrieveResponse(BaseModel):
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int
