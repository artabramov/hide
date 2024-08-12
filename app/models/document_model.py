from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Float
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

    original_filename = Column(String(256), index=True)
    document_filename = Column(String(256), index=True, unique=True)
    document_filesize = Column(BigInteger, index=True)
    document_mimetype = Column(String(256), index=True)
    document_width = Column(Integer, nullable=True)
    document_height = Column(Integer, nullable=True)
    document_duration = Column(Float, nullable=True)
    document_bitrate = Column(Integer, nullable=True)
    document_summary = Column(String(512), nullable=True)

    thumbnail_filename = Column(String(128), nullable=True, unique=True)
    comments_count = Column(Integer, index=True, default=0)

    document_user = relationship(
        "User", back_populates="user_documents", lazy="joined")
    document_collection = relationship(
        "Collection", back_populates="collection_documents", lazy="joined")

    def __init__(self, user_id: int, collection_id: int,
                 original_filename: str, document_filename: str,
                 document_filesize: int, document_mimetype: str,
                 document_width: int, document_height: int,
                 document_duration: float, document_bitrate: int,
                 document_summary: str = None, thumbnail_filename: str = None):
        self.user_id = user_id
        self.collection_id = collection_id

        self.original_filename = original_filename
        self.document_filename = document_filename
        self.document_filesize = document_filesize
        self.document_mimetype = document_mimetype
        self.document_width = document_width
        self.document_height = document_height
        self.document_duration = document_duration
        self.document_bitrate = document_bitrate
        self.document_summary = document_summary

        self.thumbnail_filename = thumbnail_filename
        self.comments_count = 0

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
