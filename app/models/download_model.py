from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
import time

cfg = get_config()


class Download(Base):
    __tablename__ = "mediafiles_downloads"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    mediafile_id = Column(BigInteger, ForeignKey("mediafiles.id"), index=True)
    revision_id = Column(BigInteger, ForeignKey("mediafiles_revisions.id"),
                         index=True)

    download_user = relationship(
        "User", back_populates="user_downloads", lazy="joined")

    download_mediafile = relationship(
        "Mediafile", back_populates="mediafile_downloads", lazy="joined")

    download_revision = relationship(
        "Revision", back_populates="revision_downloads", lazy="joined")

    def __init__(self, user_id: int, mediafile_id: int, revision_id: int):
        self.user_id = user_id
        self.mediafile_id = mediafile_id
        self.revision_id = revision_id

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user_id": self.user_id,
            "mediafile_id": self.mediafile_id,
            "revision_id": self.revision_id,
            "download_user": self.download_user.to_dict(),
        }
