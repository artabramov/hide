"""
The module provides functions for validating and normalizing option
keys and values. These validators are used within Pydantic schemas.
"""

from typing import Union


def validate_option_key(option_key: str) -> str:
    """
    Validates and normalizes an option key by stripping leading and
    trailing whitespace, converting it to lowercase, and ensuring
    it is at least 2 characters long.
    """
    option_key = option_key.strip().lower()
    if len(option_key) < 2:
        raise ValueError
    return option_key


def validate_option_value(option_value: str = None) -> Union[str, None]:
    """
    Strips leading and trailing whitespace from the option value if
    the value is a string.
    """
    return option_value.strip() if option_value else None
