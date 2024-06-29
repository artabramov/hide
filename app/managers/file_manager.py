import os
import uuid
import shutil
# import filetype
import aiofiles
import aiofiles.os
from time import time
from types import SimpleNamespace
# import io
# from app.logger import get_log
# from app.config import get_cfg

# cfg = get_cfg()
# log = get_log()


class FileManager:
    """File Manager."""

    @staticmethod
    async def file_read(path: str) -> bytes:
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()

    @staticmethod
    async def file_write(path: str, data: bytes):
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)
