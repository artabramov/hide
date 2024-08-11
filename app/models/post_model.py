from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config

cfg = get_config()


class Post(Base):
    __tablename__ = "posts"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    album_id = Column(BigInteger, ForeignKey("albums.id"), index=True)

    original_filename = Column(String(256), index=True)
    post_filename = Column(String(256), index=True, unique=True)
    post_filesize = Column(BigInteger, index=True)
    post_mimetype = Column(String(256), index=True)
    post_width = Column(Integer, nullable=True)
    post_height = Column(Integer, nullable=True)
    post_duration = Column(Float, nullable=True)
    post_bitrate = Column(Integer, nullable=True)
    post_summary = Column(String(512), nullable=True)

    thumbnail_filename = Column(String(128), nullable=True, unique=True)
    comments_count = Column(Integer, index=True, default=0)

    post_user = relationship("User", back_populates="user_posts",
                             lazy="joined")
    post_album = relationship("Album", back_populates="album_posts",
                              lazy="joined")

    def __init__(self, user_id: int, album_id: int, original_filename: str,
                 post_filename: str, post_filesize: int, post_mimetype: str,
                 post_width: int, post_height: int, post_duration: float,
                 post_bitrate: int, post_summary: str = None,
                 thumbnail_filename: str = None):
        self.user_id = user_id
        self.album_id = album_id

        self.original_filename = original_filename
        self.post_filename = post_filename
        self.post_filesize = post_filesize
        self.post_mimetype = post_mimetype
        self.post_width = post_width
        self.post_height = post_height
        self.post_duration = post_duration
        self.post_bitrate = post_bitrate
        self.post_summary = post_summary

        self.thumbnail_filename = thumbnail_filename
        self.comments_count = 0

    def to_dict(self):
        return {
            # "id": self.id,
            # "created_date": self.created_date,
            # "updated_date": self.updated_date,
            # "user_id": self.user_id,
            # "album_id": self.album_id,

            # "post_type": self.post_type.name,
            # "filesize": self.filesize,
            # "mimetype": self.mimetype,
            # "width": self.width,
            # "height": self.height,
            # "duration": self.duration,
        }
