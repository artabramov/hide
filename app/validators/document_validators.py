"""
The module provides functions for validating document attributes,
such as document summary. The validator is used within Pydantic schemas.
"""

from typing import Union


def validate_document_summary(document_summary: str = None) -> Union[str, None]:  # noqa E501
    """
    Strips leading and trailing whitespace from the document summary
    if it provided.
    """
    return document_summary.strip() if document_summary else None
