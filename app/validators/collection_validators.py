"""
The module provides functions for validating collection attributes,
such as collection name and collection summary. These validators are
used within Pydantic schemas.
"""

from typing import Union


def validate_collection_name(collection_name: str) -> str:
    """
    Validates that the collection name is at least 2 characters long
    after stripping leading and trailing whitespace.
    """
    if len(collection_name.strip()) < 2:
        raise ValueError
    return collection_name.strip()


def validate_collection_summary(collection_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strips leading and trailing whitespace from the collection summary
    if it provided.
    """
    return collection_summary.strip() if collection_summary else None
