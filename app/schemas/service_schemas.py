
from pydantic import BaseModel


class LockResponse(BaseModel):
    is_locked: bool


class UnlockResponse(BaseModel):
    is_locked: bool


class HelloResponse(BaseModel):
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int
    is_locked: bool
