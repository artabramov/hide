"""
The module provides functionality for managing a lock file to control
access to system resources. It includes utilities for checking if the
system is locked, creating or removing a lock file asynchronously, and
a decorator to enforce locking on FastAPI routers.
"""

import functools
import os
import time
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


def get_lock_time():
    lock_time = 0
    if is_locked():
        lock_created = os.path.getctime(cfg.LOCK_FILE_PATH)
        lock_time = int(time.time() - lock_created)
    return lock_time


async def lock():
    """
    Creates a lock file if the system is not already locked. The lock
    file is used to prevent concurrent access or indicate a restricted
    state. The function only writes the lock file if it does not
    already exist.
    """
    if not is_locked():
        await FileManager.write(cfg.LOCK_FILE_PATH, bytes())


async def unlock():
    """
    Removes the lock file if it exists, thereby unlocking the system.
    The function only deletes the lock file if the system is currently
    locked. This is typically used to signal the end of a restricted
    state or maintenance period.
    """
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
            raise HTTPException(status_code=423)
        return await func(*args, **kwargs)
    return wrapped
