"""
The module provides functions for validating and normalizing option
keys and values. These validators are used within Pydantic schemas.
"""

from typing import Union


def validate_option_key(option_key: str) -> str:
    """
    Validates and normalizes an option key by stripping leading and
    trailing whitespace, and converting it to lowercase.
    """
    return option_key.strip().lower()


def validate_option_value(option_value: str = None) -> Union[str, None]:
    """
    Strips leading and trailing whitespace from the option value if
    the value is a string.
    """
    return option_value.strip() if option_value else None
