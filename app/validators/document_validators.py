"""
The module provides functions for validating document attributes,
such as document summary. The validator is used within Pydantic schemas.
"""

from typing import Union


def validate_document_name(document_name: str = None) -> Union[str, None]:
    """
    Validates and normalizes a document name by stripping leading and
    trailing whitespace. If the input is empty, it returns none.
    Otherwise, it returns the trimmed document name.
    """
    return document_name.strip() if document_name else None


def validate_document_summary(document_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strips leading and trailing whitespace from the document summary
    if it provided.
    """
    return document_summary.strip() if document_summary else None
