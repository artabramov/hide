"""
The module provides functions for validating collection attributes,
such as collection name and collection summary. These validators are
used within Pydantic schemas.
"""

from typing import Union


def validate_collection_name(collection_name: str) -> str:
    """
    Strips leading and trailing whitespace.
    """
    return collection_name.strip()


def validate_collection_summary(collection_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Validates and normalizes a collection summary. If there is no input,
    or if the input is an empty string or consists only of whitespace,
    it returns none. Otherwise, it returns the trimmed user signature.
    """
    if collection_summary is None:
        return None

    collection_summary = collection_summary.strip()
    return None if collection_summary == "" else collection_summary
