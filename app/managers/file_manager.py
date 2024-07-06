# import os
# import uuid
# import shutil
# import filetype
import aiofiles
import aiofiles.os
# from time import time
# from types import SimpleNamespace
from app.decorators.timed_deco import timed
# import io
# from app.logger import get_log
# from app.config import get_cfg

# cfg = get_cfg()
# log = get_log()


class FileManager:
    """File Manager."""

    @staticmethod
    @timed
    async def write(path: str, data: bytes):
        """Write file."""
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)

    @staticmethod
    @timed
    async def read(path: str) -> bytes:
        """Read file."""
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()
