"""
The module provides functions for validating comment attributes,
such as comment content. The validator is used within Pydantic schemas.
"""


def validate_comment_content(comment_content: str) -> str:
    """
    Validates and normalizes a comment content by stripping leading and
    trailing whitespace. If the input is empty, it returns none.
    Otherwise, it returns the trimmed comment content.
    """
    return comment_content.strip() if comment_content else None
