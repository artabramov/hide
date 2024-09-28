import time
from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Tag(Base):
    __tablename__ = "mediafiles_tags"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    mediafile_id = Column(BigInteger, ForeignKey("mediafiles.id"),
                          nullable=False, index=True)
    tag_value = Column(String(256), nullable=False, index=True)

    tag_mediafile = relationship("Mediafile", back_populates="mediafile_tags",
                                 lazy="noload")

    def __init__(self, mediafile_id: int, tag_value: str):
        self.mediafile_id = mediafile_id
        self.tag_value = tag_value
