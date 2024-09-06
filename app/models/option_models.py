from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from time import time

cfg = get_config()


class Option(Base):
    __tablename__ = "options"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    option_key = Column(String(40), nullable=False, index=True, unique=True)
    option_value = Column(String(512), nullable=False, index=True)

    option_user = relationship(
        "User", back_populates="user_options", lazy="joined")

    def __init__(self, user_id: int, option_key: str, option_value: str):
        self.user_id = user_id
        self.option_key = option_key
        self.option_value = option_value

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "option_key": self.option_value,
            "option_value": self.option_value,
            "comment_user": self.comment_user.to_dict(),
        }
