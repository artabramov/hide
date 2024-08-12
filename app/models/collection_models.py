from sqlalchemy import (Boolean, Column, BigInteger, Integer, ForeignKey,
                        String)
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from time import time

cfg = get_config()


class Collection(Base):
    __tablename__ = "collections"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    is_locked = Column(Boolean)
    collection_name = Column(String(128), index=True, unique=True)
    collection_summary = Column(String(512), nullable=True)
    posts_count = Column(Integer, index=True, default=0)
    posts_size = Column(BigInteger, index=True, default=0)

    collection_user = relationship("User", back_populates="user_collections",
                                   lazy="joined")
    collection_posts = relationship("Post", back_populates="post_collection",
                                    lazy="noload")

    def __init__(self, user_id: int, is_locked: bool, collection_name: str,
                 collection_summary: str = None):
        self.user_id = user_id
        self.is_locked = is_locked
        self.collection_name = collection_name
        self.collection_summary = collection_summary
        self.posts_count = 0
        self.posts_size = 0

    def to_dict(self):
        # self.collection_user
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "is_locked": self.is_locked,
            "collection_name": self.collection_name,
            "collection_summary": self.collection_summary,
            "posts_count": self.posts_count,
            "posts_size": self.posts_size,
        }
