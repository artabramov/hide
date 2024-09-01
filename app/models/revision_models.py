import os
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config

cfg = get_config()


class Revision(Base):
    __tablename__ = "documents_revisions"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)

    revision_filename = Column(String(256), nullable=False, unique=True)
    revision_size = Column(BigInteger, index=False, nullable=False)
    original_filename = Column(String(256), nullable=False)
    original_size = Column(BigInteger, index=True, nullable=False)
    original_mimetype = Column(String(256), index=True, nullable=False)
    thumbnail_filename = Column(String(80), nullable=True, unique=True)
    downloads_count = Column(Integer, index=True, default=0)

    revision_user = relationship(
        "User", back_populates="user_revisions", lazy="joined")

    revision_document = relationship(
        "Document", back_populates="document_revisions", lazy="joined",
        foreign_keys=document_id, remote_side="Document.id")

    def __init__(self, user_id: int, document_id: int, revision_filename: str,
                 revision_size: int, original_filename: str, original_size: int, # noqa E501
                 original_mimetype: str, thumbnail_filename: str = None):
        self.user_id = user_id
        self.document_id = document_id
        self.revision_filename = revision_filename
        self.revision_size = revision_size
        self.original_filename = original_filename
        self.original_size = original_size
        self.original_mimetype = original_mimetype
        self.thumbnail_filename = thumbnail_filename
        self.downloads_count = 0

    @property
    def path(self):
        return os.path.join(cfg.REVISIONS_BASE_PATH, self.encrypted_filename)

    @property
    def thumbnail_url(self):
        if self.thumbnail_filename:
            return cfg.THUMBNAILS_BASE_URL + self.thumbnail_filename

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "revision_size": self.revision_size,
            "original_filename": self.original_filename,
            "original_size": self.original_size,
            "original_mimetype": self.original_mimetype,
            "thumbnail_url": self.thumbnail_url,
            "downloads_count": self.downloads_count,
        }
