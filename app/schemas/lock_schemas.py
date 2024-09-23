
from pydantic import BaseModel


class LockRetrieveResponse(BaseModel):
    is_locked: bool
    locked_time: int


class LockCreateResponse(BaseModel):
    is_locked: bool


class LockDeleteResponse(BaseModel):
    is_locked: bool
