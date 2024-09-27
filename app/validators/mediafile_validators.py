from typing import Union


def validate_mediafile_name(mediafile_name: str) -> str:
    """
    Validates and normalizes a mediafile name by stripping leading and
    trailing whitespace.
    """
    return mediafile_name.strip() if mediafile_name else None


def validate_mediafile_summary(mediafile_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strips leading and trailing whitespace from the mediafile summary
    if it provided.
    """
    return mediafile_summary.strip() if mediafile_summary else None


def validate_tags(tags: str = None) -> Union[str, None]:
    return tags.strip().lower() if tags else None
