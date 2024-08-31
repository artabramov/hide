import os
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config

cfg = get_config()


class Upload(Base):
    __tablename__ = "documents_uploads"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), index=True)

    original_filename = Column(String(256), index=True, nullable=False)
    encrypted_filename = Column(String(256), index=False, nullable=False,
                                unique=True)

    original_filesize = Column(BigInteger, index=True, nullable=False)
    encrypted_filesize = Column(BigInteger, index=False, nullable=False)

    mimetype = Column(String(256), index=True, nullable=False)
    thumbnail_filename = Column(String(80), nullable=True, unique=True)
    downloads_count = Column(Integer, index=True, default=0)

    upload_user = relationship(
        "User", back_populates="user_uploads", lazy="joined")

    upload_document = relationship(
        "Document", back_populates="document_uploads", lazy="joined")

    def __init__(self, user_id: int, document_id: int,
                 original_filename: str, encrypted_filename: str,
                 original_filesize: int, encrypted_filesize: int,
                 mimetype: str, thumbnail_filename: str = None):
        self.user_id = user_id
        self.document_id = document_id
        self.original_filename = original_filename
        self.encrypted_filename = encrypted_filename
        self.original_filesize = original_filesize
        self.encrypted_filesize = encrypted_filesize
        self.mimetype = mimetype
        self.thumbnail_filename = thumbnail_filename
        self.downloads_count = 0

    @property
    def path(self):
        return os.path.join(cfg.UPLOADS_BASE_PATH, self.encrypted_filename)

    @property
    def thumbnail_url(self):
        if self.thumbnail_filename:
            return cfg.THUMBNAILS_BASE_URL + self.thumbnail_filename

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "original_filename": self.original_filename,
            "encrypted_filename": self.encrypted_filename,
            "original_filesize": self.original_filesize,
            "encrypted_filesize": self.encrypted_filesize,
            "mimetype": self.mimetype,
            "thumbnail_url": self.thumbnail_url,
            "downloads_count": self.downloads_count,
        }
