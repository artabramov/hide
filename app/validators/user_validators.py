"""
The module provides functions for validating user entity attributes,
such as login, password, first name, last name, TOTP (Time-based
One-Time Password), and token expiration time. These validators are
used within Pydantic schemas.
"""

from typing import Union


def validate_user_login(user_login: str) -> str:
    """
    Normalizes the user login by stripping leading and trailing
    whitespace and converting it to lowercase.
    """
    return user_login.strip().lower()


def validate_first_name(first_name: str) -> str:
    return first_name.strip()


def validate_last_name(last_name: str) -> str:
    """
    Validates the user last name to ensure it is at least 2 characters
    long after stripping leading and trailing whitespace.
    """
    return last_name.strip()


def validate_user_signature(user_signature: str = None) -> Union[str, None]:
    """
    Validates and normalizes a user signature. If there is no input, or
    if the input is an empty string or consists only of whitespace, it
    returns none. Otherwise, it returns the trimmed user signature.
    """
    if user_signature is None:
        return None

    user_signature = user_signature.strip()
    return None if user_signature == "" else user_signature


def validate_user_contacts(user_contacts: str = None) -> Union[str, None]:
    """
    Validates and normalizes a user contacts. If there is no input, or
    if the input is an empty string or consists only of whitespace, it
    returns none. Otherwise, it returns the trimmed user contacts.
    """
    if user_contacts is None:
        return None

    user_contacts = user_contacts.strip()
    return None if user_contacts == "" else user_contacts


def validate_user_totp(user_totp: str) -> str:
    """
    Validates the user TOTP (Time-based One-Time Password) to ensure
    it is numeric.
    """
    if not user_totp.isnumeric():
        raise ValueError
    return user_totp
