import os
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config

cfg = get_config()


class Document(Base):
    __tablename__ = "documents"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    collection_id = Column(BigInteger, ForeignKey("collections.id"),
                           index=True)

    document_name = Column(String(256), index=True, nullable=False)
    document_summary = Column(String(512), nullable=True)

    filename = Column(String(256), index=True, nullable=False, unique=True)
    filesize = Column(BigInteger, index=True, nullable=False)
    mimetype = Column(String(256), index=True, nullable=False)

    thumbnail_filename = Column(String(128), nullable=True, unique=True)
    comments_count = Column(Integer, index=True, default=0)

    document_user = relationship(
        "User", back_populates="user_documents", lazy="joined")
    document_collection = relationship(
        "Collection", back_populates="collection_documents", lazy="joined")

    def __init__(self, user_id: int, collection_id: int, document_name: str,
                 filename: str, filesize: int, mimetype: str,
                 document_summary: str = None, thumbnail_filename: str = None):
        self.user_id = user_id
        self.collection_id = collection_id

        self.document_name = document_name
        self.document_summary = document_summary

        self.filename = filename
        self.filesize = filesize
        self.mimetype = mimetype

        self.thumbnail_filename = thumbnail_filename
        self.comments_count = 0

    @property
    def file_path(self):
        return os.path.join(cfg.DOCUMENTS_BASE_PATH, self.filename)

    def to_dict(self):
        return {
            # "id": self.id,
            # "created_date": self.created_date,
            # "updated_date": self.updated_date,
            # "user_id": self.user_id,
            # "collection_id": self.collection_id,

            # "document_type": self.document_type.name,
            # "filesize": self.filesize,
            # "mimetype": self.mimetype,
            # "width": self.width,
            # "height": self.height,
            # "duration": self.duration,
        }
