"""
This module defines the SQLAlchemy model for recording document
downloads. The Download class tracks details of each download, including
the user and document involved. It includes attributes for the download
ID, creation date, user ID, and document ID, and establishes
relationships with the User and Document models. The class also provides
methods for initializing an instance and converting it to a dictionary
format.
"""

from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from time import time

cfg = get_config()


class Download(Base):
    """
    Represents a record of a document download, including the user who
    initiated the download and the document that was downloaded.
    Contains fields for the download ID, creation date, user ID, and
    document ID. Relationships are established with the user and
    document models, with methods to initialize the object and convert
    it to a dictionary representation.
    """
    __tablename__ = "downloads"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)

    download_user = relationship(
        "User", back_populates="user_downloads", lazy="joined")

    download_document = relationship(
        "Document", back_populates="document_downloads", lazy="noload")

    def __init__(self, user_id: int, document_id: int):
        self.user_id = user_id
        self.document_id = document_id

    def to_dict(self):
        """
        Converts the object to a dictionary format, including the ID,
        creation date, user ID, document ID, and a dictionary
        representation of the associated user object. This method
        provides a structured representation of the object suitable
        for serialization.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "download_user": self.download_user.to_dict(),
        }
