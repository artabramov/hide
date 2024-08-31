"""
Provides asynchronous functionality for image resizing and video frame
extraction. Image resizing and video frame freezing operations are
performed synchronously in separate threads to avoid blocking the event
loop. This module includes functions for resizing images, extracting
thumbnails from videos, and creating image thumbnails with specified
dimensions and quality. It integrates with the Pillow library for image
processing and FFmpeg for video frame extraction.
"""

import os
import uuid
import asyncio
import ffmpeg
from typing import Union
from PIL import Image
from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()


def _image_resize_sync(path: str, width: int, height: int, quality: int):
    """
    Resizes an image to the specified width and height and saves it with
    the given quality. This function opens the image from the provided
    path, resizes it while maintaining the aspect ratio, and saves it
    with the specified quality.
    """
    im = Image.open(path)
    im.thumbnail((width, height))
    im.save(path, quality=quality)


async def image_resize(path: str, width: int, height: int, quality: int):
    """
    Asynchronously resizes an image to the specified width and height,
    and saves it with the given quality. The actual resizing is
    performed synchronously in a separate thread.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _image_resize_sync, path,
                               width, height, quality)


def _video_freeze_sync(src_path: str, dst_path: str):
    """
    Freezes the first frame of a video and saves it as an image
    file using FFmpeg.
    """
    output = ffmpeg.input(src_path, ss=0).output(dst_path, vframes=1)
    output.overwrite_output().run(capture_stdout=True, capture_stderr=True)


async def video_freeze(src_path: str, dst_path: str):
    """
    Asynchronously freezes the first frame of a video and saves it as an
    image file by calling the synchronous _video_freeze_sync function
    within an executor.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _video_freeze_sync, src_path, dst_path)


async def thumbnail_create(path: str, mimetype: str) -> Union[str, None]:
    """
    Generates a thumbnail for the given file based on its MIME type,
    creating an image thumbnail from images or extracting a frame from
    videos, and resizing it to specified dimensions. Returns the
    filename of the created thumbnail if successful, otherwise returns
    None. Handles both image and video files, with appropriate error
    handling and logging for issues during thumbnail creation.
    """
    is_image = FileManager.is_image(mimetype)
    is_video = FileManager.is_video(mimetype) if not is_image else False

    thumbnail_filename = None
    if is_image or is_video:

        thumbnail_filename = str(uuid.uuid4()) + cfg.THUMBNAILS_EXTENSION
        thumbnail_path = os.path.join(cfg.THUMBNAILS_BASE_PATH,
                                      thumbnail_filename)

        try:
            if is_image:
                await FileManager.copy(path, thumbnail_path)

            elif is_video:
                await video_freeze(path, thumbnail_path)

            await image_resize(thumbnail_path, cfg.THUMBNAIL_WIDTH,
                               cfg.THUMBNAIL_HEIGHT, cfg.THUMBNAIL_QUALITY)

        except Exception:
            pass

    return thumbnail_filename
