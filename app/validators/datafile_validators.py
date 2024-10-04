from typing import Union


def validate_datafile_name(datafile_name: str) -> str:
    """
    Validates and normalizes a datafile name by stripping leading and
    trailing whitespace.
    """
    return datafile_name.strip() if datafile_name else None


def validate_datafile_summary(datafile_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strips leading and trailing whitespace from the datafile summary
    if it provided.
    """
    return datafile_summary.strip() if datafile_summary else None


def validate_tags(tags: str = None) -> Union[str, None]:
    return tags.strip().lower() if tags else None
