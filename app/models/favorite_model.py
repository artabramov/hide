"""
This module defines the Favorite model for managing user favorites of
datafiles in the database. The Favorite class includes fields for
tracking the user who favorited a datafile, the datafile itself, and
the date when the favorite was created. It also establishes
relationships with User and datafile models and provides methods
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
    Represents a user's favorite datafile. Each favorite is linked to a
    specific user and datafile, and includes a creation timestamp.
    """
    __tablename__ = "favorites"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    datafile_id = Column(BigInteger, ForeignKey("datafiles.id"), index=True)

    favorite_user = relationship(
        "User", back_populates="user_favorites", lazy="noload")

    favorite_datafile = relationship(
        "Datafile", back_populates="datafile_favorites", lazy="joined")

    def __init__(self, user_id: int, datafile_id: int):
        """
        Initializes a Favorite instance with the specified user_id
        and datafile_id.
        """
        self.user_id = user_id
        self.datafile_id = datafile_id

    def to_dict(self):
        """
        Converts the Favorite instance to a dictionary, including
        related user and datafile details.
        """
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "datafile_id": self.datafile_id,
            "favorite_datafile": self.favorite_datafile.to_dict(),
        }
