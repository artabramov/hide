import enum
import json
from time import time
from sqlalchemy import (Column, BigInteger, Integer, ForeignKey, Enum, JSON,
                        String)
from app.models.user_models import User
from app.models.collection_models import Collection
from app.models.document_model import Document
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
    current_user: User, collection: Collection
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


async def after_document_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """Audit a document insertion."""
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
