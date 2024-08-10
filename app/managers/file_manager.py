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
from app.config import get_config

cfg = get_config()
# log = get_log()


class FileManager:

    @staticmethod
    async def upload(file: object, path: str):
        async with aiofiles.open(path, "wb") as fn:
            while content := await file.read(cfg.FILE_UPLOAD_CHUNK_SIZE):
                await fn.write(content)

    @staticmethod
    @timed
    async def write(path: str, data: bytes):
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)

    @staticmethod
    @timed
    async def read(path: str) -> bytes:
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()
