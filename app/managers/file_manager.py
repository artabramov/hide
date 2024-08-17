"""
This module provides the FileManager class, which offers asynchronous
methods for performing various file operations such as uploading,
deleting, writing, reading, encrypting, and decrypting files. It
leverages aiofiles for efficient asynchronous file I/O operations and
uses the Fernet encryption system to secure data. The methods are
designed to handle files and data asynchronously to ensure optimal
performance in high-concurrency environments.
"""

import aiofiles
import aiofiles.os
from app.decorators.timed_deco import timed
from app.config import get_config
from cryptography.fernet import Fernet

cfg = get_config()
cipher_suite = Fernet(cfg.FERNET_KEY)


class FileManager:
    """
    Provides asynchronous methods for various file operations using
    aiofiles. This includes uploading files in chunks, deleting files if
    they exist, writing data to files, reading file contents, and
    encrypting or decrypting data with a Fernet cipher. These methods
    are designed to handle I/O operations efficiently in an asynchronous
    manner to support high-performance applications.
    """

    @staticmethod
    @timed
    async def upload(file: object, path: str):
        """
        Asynchronously uploads a file to the specified path by reading
        the file in chunks and writing each chunk to the destination
        path, handling large files efficiently without loading them
        entirely into memory.
        """
        async with aiofiles.open(path, mode="wb") as fn:
            while content := await file.read(cfg.FILE_UPLOAD_CHUNK_SIZE):
                await fn.write(content)

    @staticmethod
    @timed
    async def delete(path: str):
        """
        Asynchronously deletes the file at the specified path if it
        exists, first checking for the file's existence to avoid errors.
        """
        if await aiofiles.os.path.isfile(path):
            await aiofiles.os.unlink(path)

    @staticmethod
    @timed
    async def write(path: str, data: bytes):
        """
        Asynchronously writes the given byte data to a file at the
        specified path, overwriting the file if it already exists.
        """
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)

    @staticmethod
    @timed
    async def read(path: str) -> bytes:
        """
        Asynchronously reads and returns the contents of a file at the
        specified path, loading the entire file into memory.
        """
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()

    @staticmethod
    @timed
    async def encrypt(data: bytes) -> bytes:
        """
        Asynchronously encrypts the given byte data using the configured
        Fernet cipher suite, ensuring secure data encryption.
        """
        return cipher_suite.encrypt(data)

    @staticmethod
    @timed
    async def decrypt(data: bytes) -> bytes:
        """
        Asynchronously decrypts the given byte data using the configured
        Fernet cipher suite, returning the original data.
        """
        return cipher_suite.decrypt(data)
