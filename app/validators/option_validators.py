from typing import Union


def validate_option_key(option_key: str) -> str:
    option_key = option_key.strip().lower()
    if len(option_key) < 2:
        raise ValueError
    return option_key


def validate_option_value(option_value: str = None) -> Union[str, None]:
    return option_value.strip() if option_value else None
