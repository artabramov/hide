"""
Provides asynchronous image resizing functionality using Pillow. The
resizing operation is performed synchronously in a separate thread to
avoid blocking the event loop.
"""

import asyncio
from PIL import Image


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
