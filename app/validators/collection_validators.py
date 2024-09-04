from typing import Union


def validate_collection_name(collection_name: str) -> str:
    """
    Ensure the collection name is at least 2 characters long after
    stripping extra spaces.
    """
    if len(collection_name.strip()) < 2:
        raise ValueError
    return collection_name.strip()


def validate_collection_summary(collection_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strip extra spaces from the collection summary if provided or None
    if not.
    """
    return collection_summary.strip() if collection_summary else None
