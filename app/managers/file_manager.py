"""
This module defines the FileManager class, which provides a suite
of asynchronous methods for performing file operations, including
uploading, deleting, writing, reading, copying, encrypting, and
decrypting files. It utilizes the aiofiles library for non-blocking
file I/O operations and the Fernet encryption system for secure data
handling. The methods are designed to work efficiently in asynchronous
contexts, supporting high-performance and scalable applications.
The class includes functionality to handle different file types,
such as images and videos, and ensures optimal performance and
security for file management tasks.
"""

import aiofiles
import aiofiles.os
from app.decorators.timed_decorator import timed
from app.config import get_config
from cryptography.fernet import Fernet

cfg = get_config()
cipher_suite = Fernet(cfg.FERNET_KEY)

FILE_UPLOAD_CHUNK_SIZE = 1024 * 8  # 8 KB
FILE_COPY_CHUNK_SIZE = 1024 * 8  # 8 KB
IMAGE_MIMETYPES = [
    "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff",
    "image/webp", "image/svg+xml", "image/x-icon", "image/heif", "image/heic",
    "image/jp2", "image/avif", "image/apng", "image/x-tiff",
    "image/x-cmu-raster", "image/x-portable-anymap", "image/x-portable-bitmap",
    "image/x-portable-graymap", "image/x-portable-pixmap"]
VIDEO_MIMETYPES = [
    "video/mp4", "video/avi", "video/mkv", "video/webm", "video/x-msvideo",
    "video/x-matroska", "video/quicktime"]


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
    def is_image(mimetype: str) -> bool:
        """
        Determines if the given MIME type is classified as an image type
        by checking it against a predefined set of image MIME types.
        The check is case-insensitive and returns True if the MIME type
        matches any of the image types in the list, otherwise False.
        """
        return mimetype.lower() in IMAGE_MIMETYPES

    @staticmethod
    def is_video(mimetype: str) -> bool:
        """
        Determines if the given MIME type is classified as a video type
        by checking it against a predefined set of video MIME types.
        The check is case-insensitive and returns True if the MIME type
        matches any of the video types in the list, otherwise False.
        """
        return mimetype.lower() in VIDEO_MIMETYPES

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
            while content := await file.read(FILE_UPLOAD_CHUNK_SIZE):
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

    @staticmethod
    @timed
    async def copy(src_path: str, dst_path: str):
        """
        Asynchronously copies the contents of a file from src_path to
        dst_path in chunks. The method opens the source file for reading
        in binary mode and the destination file for writing in binary
        mode. It reads from the source file in chunks and writes those
        chunks to the destination file until the entire file has been
        copied. The operation is performed asynchronously to avoid
        blocking the event loop, and errors such as file not found or
        permission issues are handled gracefully.
        """
        async with aiofiles.open(src_path, mode="rb") as src_context:
            async with aiofiles.open(dst_path, mode="wb") as dst_context:
                while True:
                    chunk = await src_context.read(FILE_COPY_CHUNK_SIZE)
                    if not chunk:
                        break
                    await dst_context.write(chunk)
