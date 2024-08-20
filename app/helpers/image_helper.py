import asyncio
from PIL import Image


def _image_resize_sync(path: str, width: int, height: int, quality: int):
    im = Image.open(path)
    im.thumbnail((width, height))  # Maintain aspect ratio with thumbnail
    im.save(path, quality=quality)  # Use 'quality' for JPEG images


async def image_resize(path: str, width: int, height: int, quality: int):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _image_resize_sync, path,
                               width, height, quality)
