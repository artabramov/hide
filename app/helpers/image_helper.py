from PIL import Image


class ImageHelper:

    @staticmethod
    async def resize(path: str, width: int, height: int, quality: int):
        im = Image.open(path)
        # width = cfg.THUMBNAIL_WIDTH
        # height = int((float(im.size[1]) / float(im.size[0])) * width)
        im.thumbnail(tuple([width, height]))
        im.save(path, image_quality=quality)
