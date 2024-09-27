"""
This module defines the Favorite model for managing user favorites of
mediafiles in the database. The Favorite class includes fields for
tracking the user who favorited a mediafile, the mediafile itself, and
the date when the favorite was created. It also establishes
relationships with User and mediafile models and provides methods
to initialize instances and convert them to dictionaries.
"""

import time
from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Favorite(Base):
    """
    Represents a user's favorite mediafile. Each favorite is linked to a
    specific user and mediafile, and includes a creation timestamp.
    """
    __tablename__ = "mediafiles_favorites"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    mediafile_id = Column(BigInteger, ForeignKey("mediafiles.id"), index=True)

    favorite_user = relationship(
        "User", back_populates="user_favorites", lazy="noload")

    favorite_mediafile = relationship(
        "Mediafile", back_populates="mediafile_favorites", lazy="joined")

    def __init__(self, user_id: int, mediafile_id: int):
        """
        Initializes a Favorite instance with the specified user_id
        and mediafile_id.
        """
        self.user_id = user_id
        self.mediafile_id = mediafile_id

    def to_dict(self):
        """
        Converts the Favorite instance to a dictionary, including
        related user and mediafile details.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "mediafile_id": self.mediafile_id,
            "favorite_mediafile": self.favorite_mediafile.to_dict(),
        }
