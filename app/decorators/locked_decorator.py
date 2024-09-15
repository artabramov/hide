"""
This module defines a decorator that enforces a lock on asynchronous
functions by checking for the presence of a lock file. The decorator
raises an 503 error if the lock file is detected, preventing the
execution of functions when the service is in a restricted state or
under maintenance.
"""

import functools
import os
from typing import Callable, Any
from fastapi import HTTPException
from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()


def is_locked():
    """
    Checks if the lock file exists at the configured path and returns
    True if it does, indicating that the system is in a locked state;
    otherwise, returns False.
    """
    return os.path.isfile(cfg.LOCK_FILE_PATH)


async def lock():
    if not is_locked():
        await FileManager.write(cfg.LOCK_FILE_PATH, bytes())


async def unlock():
    if is_locked():
        await FileManager.delete(cfg.LOCK_FILE_PATH)


def locked(func: Callable):
    """
    Decorator that enforces a lock based on the existence of a lock file
    before executing the wrapped FastAPI router. If the lock file is
    detected at the path specified in the config, a 503 error is raised.
    """
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        if is_locked():
            raise HTTPException(status_code=503)
        return await func(*args, **kwargs)
    return wrapped
