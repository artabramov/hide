import enum
import json
from time import time
from sqlalchemy import (Column, BigInteger, Integer, ForeignKey, Enum, JSON,
                        String)
from app.models.user_models import User
from app.models.collection_models import Collection
from app.database import Base
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import DeclarativeBase
from typing import List
from fastapi import Request
from app.hooks import HookAction

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


class EntityTablename(enum.Enum):
    """Database table names for entities."""
    users = "users"
    collections = "collections"


class EntityOperation(enum.Enum):
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
    hook_action = Column(Enum(HookAction), index=True)

    request_method = Column(Enum(RequestMethod), index=True)
    request_url = Column(String(256), index=True)
    query_params = Column(JSON)

    entity_operation = Column(Enum(EntityOperation), index=True)
    entity_tablename = Column(Enum(EntityTablename), index=True)
    entity_id = Column(BigInteger, index=True)
    entity_dict = Column(JSON)

    def __init__(self, current_user: User, hook_action: HookAction,
                 request: Request, entity: DeclarativeBase,
                 entity_operation: EntityOperation):
        """Initialize an instance with request and entity details."""
        self.user_id = current_user.id if current_user else None
        self.hook_action = hook_action

        self.request_method = request.method
        self.request_url = request.url.path
        self.query_params = self._to_dict(request.query_params._dict)

        self.entity_operation = entity_operation
        self.entity_tablename = EntityTablename(entity.__tablename__)
        self.entity_id = entity.id
        self.entity_dict = self._to_dict(entity.__dict__)

    def _to_dict(self, entity_dict: dict) -> json:
        """Convert a dict to string representation."""
        return {x: repr(entity_dict[x])
                if x not in OBSCURED_KEYS else OBSCURED_VALUE
                for x in entity_dict}


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
        audit = Audit(current_user, HookAction.after_user_register,
                      request, user, EntityOperation.insert)
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
    audit = Audit(current_user, HookAction.after_user_login,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_token_retrieve,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_token_invalidate,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_user_select,
                  request, user, EntityOperation.select)
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
    audit = Audit(current_user, HookAction.after_user_update,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_role_update,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_password_update,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_userpic_upload,
                  request, user, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_userpic_delete,
                  request, user, EntityOperation.update)
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
        audit = Audit(current_user, HookAction.after_users_list,
                      request, user, EntityOperation.select)
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
    audit = Audit(current_user, HookAction.after_collection_insert,
                  request, collection, EntityOperation.insert)
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
    audit = Audit(current_user, HookAction.after_collection_select,
                  request, collection, EntityOperation.select)
    await entity_manager.insert(audit)
    return collection


async def after_collection_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User, collection: Collection
) -> Collection:
    """Audit an collection updation."""
    audit = Audit(current_user, HookAction.after_collection_update,
                  request, collection, EntityOperation.update)
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
    audit = Audit(current_user, HookAction.after_collection_delete,
                  request, collection, EntityOperation.delete)
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
        audit = Audit(current_user, HookAction.after_collections_list,
                      request, collection, EntityOperation.select)
        await entity_manager.insert(audit)

    return collections
