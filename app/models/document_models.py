import os
from time import time
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.config import get_config

cfg = get_config()


class Document(Base):
    __tablename__ = "documents"
    _cacheable = True

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    updated_date = Column(Integer, index=True, onupdate=lambda: int(time()),
                          default=0)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    collection_id = Column(BigInteger, ForeignKey("collections.id"),
                           index=True)

    document_name = Column(String(128), index=True, nullable=False)
    document_summary = Column(String(512), nullable=True)
    document_size = Column(Integer, index=True, default=0)

    revisions_count = Column(Integer, index=True, default=0)
    revisions_size = Column(Integer, index=True, default=0)

    comments_count = Column(Integer, index=True, default=0)
    downloads_count = Column(Integer, index=True, default=0)
    favorites_count = Column(Integer, index=True, default=0)

    document_user = relationship(
        "User", back_populates="user_documents", lazy="joined")

    document_collection = relationship(
        "Collection", back_populates="collection_documents", lazy="joined")

    document_tags = relationship(
        "Tag", back_populates="tag_document", lazy="joined",
        cascade="all, delete-orphan")

    document_revisions = relationship(
        "Revision", back_populates="revision_document", lazy="joined",
        cascade="all, delete-orphan")

    # document_revisions = relationship(
    #     "Revision", back_populates="revision_document", lazy="noload",
    #     cascade="all, delete-orphan", foreign_keys="[Revision.document_id]"
    # )

    # document_revisions = relationship(
    #     "Revision", back_populates="revision_document", lazy="noload",
    #     cascade="all, delete-orphan")

    # document_revisions = relationship(
    #     "Revision", back_populates="revision_document", lazy="noload",
    #     cascade="all, delete-orphan", foreign_keys="Revision.document_id")

    # document_revisions = relationship(
    #     "Revision", back_populates="revision_document", lazy="noload",
    #     cascade="all, delete-orphan", foreign_keys=["Revision.document_id"])

    document_comments = relationship(
        "Comment", back_populates="comment_document", lazy="joined",
        cascade="all, delete-orphan")

    document_downloads = relationship(
        "Download", back_populates="download_document", lazy="noload",
        cascade="all, delete-orphan")

    document_favorites = relationship(
        "Favorite", back_populates="favorite_document", lazy="noload",
        cascade="all, delete-orphan")

    # last_revision = relationship(
    #     "Revision", primaryjoin="Document.last_revision_id == Revision.id",
    #     lazy="joined", uselist=False)

    def __init__(self, user_id: int, collection_id: int,
                 document_name: str, document_summary: str = None):
        self.user_id = user_id
        self.collection_id = collection_id

        self.document_name = document_name
        self.document_summary = document_summary
        self.document_size = 0

        self.revisions_count = 0
        self.revisions_size = 0

        self.comments_count = 0
        self.downloads_count = 0
        self.favorites_count = 0

    @property
    def file_path(self):
        return os.path.join(cfg.REVISIONS_BASE_PATH, self.filename)

    @property
    def tag_values(self) -> list:
        if self.document_tags:
            return [x.tag_value for x in self.document_tags]
        return []

    def to_dict(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id,
            "collection_id": self.collection_id,

            "document_name": self.document_name,
            "document_summary": self.document_summary,
            "document_size": self.document_size,

            "revisions_count": self.revisions_count,
            "revisions_size": self.revisions_size,

            "comments_count": self.comments_count,
            "downloads_count": self.downloads_count,
            "favorites_count": self.favorites_count,

            "document_tags": self.tag_values,
            # "last_revision": self.last_revision.to_dict(),
        }
