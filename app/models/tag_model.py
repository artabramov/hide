import time
from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base

cfg = get_config()


class Tag(Base):
    __tablename__ = "datafiles_tags"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    datafile_id = Column(BigInteger, ForeignKey("datafiles.id"),
                          nullable=False, index=True)
    tag_value = Column(String(256), nullable=False, index=True)

    tag_datafile = relationship("Datafile", back_populates="datafile_tags",
                                 lazy="noload")

    def __init__(self, datafile_id: int, tag_value: str):
        self.datafile_id = datafile_id
        self.tag_value = tag_value
