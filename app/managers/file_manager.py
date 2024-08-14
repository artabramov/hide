import aiofiles
import aiofiles.os
from app.decorators.timed_deco import timed
from app.config import get_config
from cryptography.fernet import Fernet

cfg = get_config()
cipher_suite = Fernet(cfg.FERNET_KEY)


class FileManager:
    """
    Provides asynchronous methods for file operations, including
    uploading, deleting, writing, and reading files. All methods handle
    files in an asynchronous manner using aiofiles to ensure efficient
    I/O operations.
    """

    @staticmethod
    @timed
    async def upload(file: object, path: str):
        """
        Asynchronously upload a file to the specified path in chunks.
        Read the file in chunks and write each chunk to the specified
        path.
        """
        async with aiofiles.open(path, mode="wb") as fn:
            while content := await file.read(cfg.FILE_UPLOAD_CHUNK_SIZE):
                await fn.write(content)

    @staticmethod
    @timed
    async def delete(path: str):
        """
        Asynchronously delete a file at the specified path if it exists.
        """
        if await aiofiles.os.path.isfile(path):
            await aiofiles.os.unlink(path)

    @staticmethod
    @timed
    async def write(path: str, data: bytes):
        """
        Asynchronously write data to a file at the specified path.
        """
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)

    @staticmethod
    @timed
    async def read(path: str) -> bytes:
        """
        Asynchronously read and return the contents of a file at the
        specified path.
        """
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()

    @staticmethod
    @timed
    async def encrypt(data: bytes) -> bytes:
        return cipher_suite.encrypt(data)

    @staticmethod
    @timed
    async def decrypt(data: bytes) -> bytes:
        return cipher_suite.decrypt(data)
