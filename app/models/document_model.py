import os
import time
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, and_
from sqlalchemy.orm import relationship
from app.models.upload_model import Upload
from app.database import Base
from app.config import get_config

cfg = get_config()


class Document(Base):
    __tablename__ = "documents"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    updated_date = Column(Integer, index=True,
                          onupdate=lambda: int(time.time()), default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True,
                     nullable=False)
    collection_id = Column(BigInteger, ForeignKey("collections.id"),
                           index=True, nullable=True)

    document_name = Column(String(256), nullable=True)
    document_summary = Column(String(512), nullable=True)

    comments_count = Column(Integer, index=True, default=0)
    uploads_count = Column(Integer, index=True, default=0)
    uploads_size = Column(Integer, index=True, default=0)
    downloads_count = Column(Integer, index=True, default=0)
    downloads_size = Column(Integer, index=True, default=0)

    document_user = relationship(
        "User", back_populates="user_documents", lazy="joined")

    document_collection = relationship(
        "Collection", back_populates="collection_documents", lazy="joined")

    document_tags = relationship(
        "Tag", back_populates="tag_document", lazy="joined",
        cascade="all, delete-orphan")

    document_uploads = relationship(
        "Upload", back_populates="upload_document",
        cascade="all, delete-orphan", foreign_keys="Upload.document_id")

    document_comments = relationship(
        "Comment", back_populates="comment_document",
        cascade="all, delete-orphan")

    document_downloads = relationship(
        "Download", back_populates="download_document",
        cascade="all, delete-orphan")

    document_favorites = relationship(
        "Favorite", back_populates="favorite_document",
        cascade="all, delete-orphan")

    latest_upload = relationship(
        "Upload", primaryjoin=and_(
            id == Upload.document_id, Upload.is_latest == True),  # noqa E712
        lazy="joined", uselist=False)

    def __init__(self, user_id: int, document_name: str,
                 collection_id: int = None, uploads_count: int = 0,
                 uploads_size: int = 0):
        self.user_id = user_id
        self.document_name = document_name
        self.collection_id = collection_id
        self.comments_count = 0
        self.uploads_count = uploads_count
        self.uploads_size = uploads_size
        self.downloads_count = 0
        self.downloads_size = 0

    @property
    def is_locked(self) -> bool:
        return self.collection_id and self.document_collection.is_locked

    @property
    def file_path(self):
        return os.path.join(cfg.UPLOADS_BASE_PATH, self.filename)

    @property
    def tag_values(self) -> list:
        if self.document_tags:
            return [x.tag_value for x in self.document_tags]
        return []

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "collection_id": self.collection_id,

            "document_name": self.document_name,
            "document_summary": self.document_summary,

            "comments_count": self.comments_count,
            "uploads_count": self.uploads_count,
            "uploads_size": self.uploads_size,
            "downloads_count": self.downloads_count,
            "downloads_size": self.downloads_size,

            "document_tags": self.tag_values,
            "document_user": self.document_user.to_dict(),
            "latest_upload": self.latest_upload.to_dict(),
        }
