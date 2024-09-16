
from pydantic import BaseModel


class SystemHelloResponse(BaseModel):
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int
    is_locked: bool


class SystemLockResponse(BaseModel):
    is_locked: bool


class SystemUnlockResponse(BaseModel):
    is_locked: bool
