"""
The module provides functions for validating comment attributes,
such as comment content. The validator is used within Pydantic schemas.
"""


def validate_comment_content(comment_content: str) -> str:
    """
    Validates and trims the comment content, ensuring it is at least 2
    characters long after removing leading and trailing whitespace.
    """
    if len(comment_content.strip()) < 2:
        raise ValueError
    return comment_content.strip()
