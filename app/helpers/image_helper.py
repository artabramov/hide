from PIL import Image


class ImageHelper:

    @staticmethod
    async def resize(path: str, width: int, height: int, quality: int):
        im = Image.open(path)
        im.thumbnail(tuple([width, height]))
        im.save(path, image_quality=quality)
