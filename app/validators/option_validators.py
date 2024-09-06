"""
The module provides functions for validating and normalizing option keys
and values, and these validators are used within Pydantic schemas.
"""

from typing import Union


def validate_option_key(option_key: str) -> str:
    """
    Validates and normalizes an option key by trimming whitespace,
    converting it to lowercase, and ensuring it is at least 2 characters
    long. If the key does not meet the length requirement, a value error
    is raised.
    """
    option_key = option_key.strip().lower()
    if len(option_key) < 2:
        raise ValueError
    return option_key


def validate_option_value(option_value: str = None) -> Union[str, None]:
    """
    Strips whitespace from the given option value if it is not None or
    an empty string. Returns the cleaned value if it exists, or None if
    the input is None or an empty string.
    """
    return option_value.strip() if option_value else None
