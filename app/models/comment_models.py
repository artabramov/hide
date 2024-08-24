from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from time import time

cfg = get_config()


class Comment(Base):
    __tablename__ = "comments"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    document_id = Column("document_id", BigInteger, ForeignKey("documents.id"),
                         index=True)
    comment_content = Column(String(512), nullable=False, index=True)

    comment_document = relationship(
        "Document", back_populates="document_comments", lazy="noload")

    def __init__(self, document_id: int, comment_content: str):
        self.document_id = document_id
        self.comment_content = comment_content
