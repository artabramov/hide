from time import time
from sqlalchemy import Integer, BigInteger
from sqlalchemy.orm import mapped_column
from app.postgres import Base
import os
from app.config import get_config

cfg = get_config()


class Basic(Base):
    __abstract__ = True
    id = mapped_column(BigInteger, primary_key=True, sort_order=-3)
    created_date = mapped_column(Integer, index=True,
                                 default=lambda: int(time()), sort_order=-2)
    updated_date = mapped_column(Integer, index=True, default=0,
                                 onupdate=lambda: int(time()), sort_order=-1)

    @property
    def dump_path(self):
        filename = "%s.%s" % (self.id, cfg.SYNC_FILE_EXT)
        return os.path.join(cfg.SYNC_BASE_PATH, self.__tablename__, filename)
