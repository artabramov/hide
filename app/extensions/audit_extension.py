import enum
import json
from time import time
from sqlalchemy import (Column, BigInteger, Integer, ForeignKey, Enum, JSON,
                        String)
from app.models.user_models import User
from app.models.collection_models import Collection
from app.models.document_models import Document
from app.models.comment_models import Comment
from app.models.download_models import Download
from app.models.favorite_models import Favorite
from app.database import Base
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import DeclarativeBase
from typing import List
from fastapi import Request

AFTER_USER_REGISTER_ENABLED = True

OBSCURED_KEYS = ["user_password", "current_password", "updated_password",
                 "user_totp", "password_hash", "mfa_secret_encrypted",
                 "jti_encrypted"]
OBSCURED_VALUE = "*" * 6


class RequestMethod(enum.Enum):
    """HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class AuditAction(enum.Enum):
    """Types of operations performed on entities."""
    insert = "insert"
    select = "select"
    update = "update"
    delete = "delete"


class Audit(Base):
    """Model for logging audit records."""
    __tablename__ = "audits"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)

    request_method = Column(Enum(RequestMethod), index=True)
    request_url = Column(String(256), index=True)
    query_params = Column(JSON)

    audit_action = Column(Enum(AuditAction), index=True)
    entity_tablename = Column(String(128), index=True)
    entity_id = Column(BigInteger, index=True)
    entity_dict = Column(JSON)

    def __init__(self, current_user: User, request: Request,
                 entity: DeclarativeBase, audit_action: AuditAction):
        """Initialize an instance with request and entity details."""
        self.user_id = current_user.id if current_user else None
        self.request_method = request.method
        self.request_url = request.url.path
        self.query_params = self._to_dict(request.query_params._dict)
        self.audit_action = audit_action

        self.entity_tablename = entity.__tablename__
        self.entity_id = entity.id
        self.entity_dict = self._to_dict(entity.__dict__)

    def _to_dict(self, entity_dict: dict) -> json:
        """Convert a dict to string representation."""
        return {x: repr(entity_dict[x])
                if x not in OBSCURED_KEYS else OBSCURED_VALUE
                for x in entity_dict if not x.startswith("_")}


async def after_startup(
    entity_manager: EntityManager,
    cache_manager: CacheManager, request: None,
    current_user: None,
    entity: None
):
    """Audit the application startup."""
    ...


async def after_user_register(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a user registration."""
    if AFTER_USER_REGISTER_ENABLED:
        audit = Audit(current_user, request, user, AuditAction.insert)
        await entity_manager.insert(audit)
    return user


async def after_user_login(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a user authentication."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_token_retrieve(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a token retrieval."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_token_invalidate(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a token invalidation."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_user_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a user selection."""
    audit = Audit(current_user, request, user, AuditAction.select)
    await entity_manager.insert(audit)
    return user


async def after_user_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a user updation."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_role_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a user role updation."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_password_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a user password updation."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_userpic_upload(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a userpic uploading."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_userpic_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """Audit a userpic deletion."""
    audit = Audit(current_user, request, user, AuditAction.update)
    await entity_manager.insert(audit)
    return user


async def after_users_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    users: List[Collection]
) -> List[Collection]:
    """Audit users list selection."""
    for user in users:
        audit = Audit(current_user, request, user, AuditAction.select)
        await entity_manager.insert(audit)
    return users


async def after_collection_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """Audit an collection insertion."""
    audit = Audit(current_user, request, collection, AuditAction.insert)
    await entity_manager.insert(audit)
    return collection


async def after_collection_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """Audit an collection selection."""
    audit = Audit(current_user, request, collection, AuditAction.select)
    await entity_manager.insert(audit)
    return collection


async def after_collection_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """Audit an collection updation."""
    audit = Audit(current_user, request, collection, AuditAction.update)
    await entity_manager.insert(audit)
    return collection


async def after_collection_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """Audit an collection deletion."""
    audit = Audit(current_user, request, collection, AuditAction.delete)
    await entity_manager.insert(audit)
    return collection


async def after_collections_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collections: List[Collection]
) -> List[Collection]:
    """Audit collections list selection."""
    for collection in collections:
        audit = Audit(current_user, request, collection, AuditAction.select)
        await entity_manager.insert(audit)
    return collections


async def after_document_upload(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """Audit a document uploading."""
    audit = Audit(current_user, request, document, AuditAction.insert)
    await entity_manager.insert(audit)
    return document


async def after_document_download(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """Audit a document downloading."""
    audit = Audit(current_user, request, document, AuditAction.select)
    await entity_manager.insert(audit)
    return document


async def after_document_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """Audit a document selecting."""
    audit = Audit(current_user, request, document, AuditAction.select)
    await entity_manager.insert(audit)
    return document


async def after_comment_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Audits the comment insertion by recording an audit entry with user
    and request details, then returns the original comment.
    """
    audit = Audit(current_user, request, comment, AuditAction.insert)
    await entity_manager.insert(audit)
    return comment


async def after_comment_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Records an audit entry for the selection of a comment, including
    details of the user and request, and returns the selected comment.
    """
    audit = Audit(current_user, request, comment, AuditAction.select)
    await entity_manager.insert(audit)
    return comment


async def after_comment_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Records an audit entry for the update of a comment, capturing user
    and request details, and returns the updated comment.
    """
    audit = Audit(current_user, request, comment, AuditAction.update)
    await entity_manager.insert(audit)
    return comment


async def after_comment_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Created an audit record for the deletion of a comment, documenting
    user and request details, and returns the deleted comment.
    """
    audit = Audit(current_user, request, comment, AuditAction.delete)
    await entity_manager.insert(audit)
    return comment


async def after_comments_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comments: List[Comment]
) -> List[Comment]:
    """
    Logs an audit entry for each comment in the list when they are
    retrieved, capturing details of the user and request, and returns
    the list of comments.
    """
    for comment in comments:
        audit = Audit(current_user, request, comment, AuditAction.select)
        await entity_manager.insert(audit)
    return comments


async def after_download_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    download: Download
) -> Download:
    """
    Audits the selection of a download by recording the action in the
    audit log. The function creates an Audit entry for the download
    selection, inserts it into the database, and returns the original
    download object.
    """
    audit = Audit(current_user, request, download, AuditAction.select)
    await entity_manager.insert(audit)
    return download


async def after_downloads_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    downloads: List[Download]
) -> List[Download]:
    """
    Audits the retrieval of a list of downloads by recording each action
    in the audit log. The function creates an Audit entry for each
    download in the list, inserts them into the database, and returns
    the original list of downloads.
    """
    for download in downloads:
        audit = Audit(current_user, request, download, AuditAction.select)
        await entity_manager.insert(audit)
    return downloads


async def after_favorite_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs an audit entry after a favorite entity is inserted and returns
    the favorite entity.
    """
    audit = Audit(current_user, request, favorite, AuditAction.insert)
    await entity_manager.insert(audit)
    return favorite


async def after_favorite_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs an audit entry for selecting a favorite entity and returns the
    favorite entity.
    """
    audit = Audit(current_user, request, favorite, AuditAction.select)
    await entity_manager.insert(audit)
    return favorite


async def after_favorite_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs an audit entry for deleting a favorite entity and returns the
    deleted favorite entity.
    """
    audit = Audit(current_user, request, favorite, AuditAction.delete)
    await entity_manager.insert(audit)
    return favorite


async def after_favorites_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorites: List[Favorite]
) -> List[Favorite]:
    """
    Logs an audit entry for each favorite entity in a list and returns
    the list of favorites.
    """
    for favorite in favorites:
        audit = Audit(current_user, request, favorite, AuditAction.select)
        await entity_manager.insert(audit)
    return favorites
