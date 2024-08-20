from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import get_config
from app.database import Base
from time import time

cfg = get_config()


class DocumentTag(Base):
    __tablename__ = "documents_tags"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    document_id = Column("document_id", BigInteger, ForeignKey("documents.id"),
                         index=True)
    tag_id = Column("tag_id", BigInteger, ForeignKey("tags.id"), index=True)

    def __init__(self, document_id: int, tag_id: int):
        self.document_id = document_id
        self.tag_id = tag_id


class Tag(Base):
    __tablename__ = "tags"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    value = Column(String(256), nullable=False, unique=True)
    documents_count = Column(Integer, index=True, default=0)

    tag_documents = relationship("Document", secondary=DocumentTag.__table__,
                                 back_populates="document_tags", lazy="noload")

    def __init__(self, value: str):
        self.value = value
        self.documents_count = 0
