from sqlalchemy import (Boolean, Column, BigInteger, Integer, ForeignKey,
                        String)
from sqlalchemy.orm import relationship
from app.config import get_config
from app.postgres import Base
from time import time

cfg = get_config()


class Folder(Base):
    __tablename__ = "folders"

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    is_locked = Column(Boolean)
    folder_name = Column(String(128), index=True, unique=True)
    folder_summary = Column(String(255), nullable=True)
    posts_count = Column(Integer, index=True, default=0)
    posts_size = Column(BigInteger, index=True, default=0)

    folder_user = relationship("User", back_populates="user_folders",
                               lazy="joined")

    def __init__(self, user_id: int, is_locked: bool, folder_name: str,
                 folder_summary: str = None):
        self.user_id = user_id
        self.is_locked = is_locked
        self.folder_name = folder_name
        self.folder_summary = folder_summary
        self.posts_count = 0
        self.posts_size = 0

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "is_locked": self.is_locked,
            "folder_name": self.folder_name,
            "folder_summary": self.folder_summary,
            "posts_count": self.posts_count,
            "posts_size": self.posts_size,
        }
