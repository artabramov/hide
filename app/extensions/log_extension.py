"""
This module contains asynchronous functions that handle post-processing
actions for various entities, including user registrations, updates, and
logins; collection and document operations; comment management; download
tracking; and favorite interactions. Each function logs specific actions
performed on these entities, capturing details about the request,
current user, and the entity involved. The log entries are inserted into
the database for audit purposes, and the functions return the processed
entity or list of entities.
"""

import enum
import json
import time
from typing import List
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (Column, BigInteger, Integer, ForeignKey, Enum,
                        JSON, String)
from fastapi import Request
from app.database import Base
from app.models.user_models import User
from app.models.collection_models import Collection
from app.models.document_models import Document
from app.models.comment_models import Comment
from app.models.download_models import Download
from app.models.favorite_models import Favorite
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager

OBSCURED_KEYS = ["user_password", "current_password", "updated_password",
                 "user_totp", "password_hash", "mfa_secret_encrypted",
                 "jti_encrypted"]
OBSCURED_VALUE = "*" * 6


class RequestMethod(enum.Enum):
    """
    Enumeration for standard HTTP request methods: GET for retrieving
    data, POST for submitting data, PUT for updating or creating
    resources, and DELETE for removing resources.
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class EntityAction(enum.Enum):
    """
    Enumeration for CRUD operations representing actions on entities:
    insert for adding new entities, select for retrieving entities,
    update for modifying existing entities, and delete for removing
    entities.
    """
    insert = "insert"
    select = "select"
    update = "update"
    delete = "delete"


class Log(Base):
    """
    Represents a log entry capturing details of operations on the
    application entities, including the request method, URL, request
    parameters, and the action performed on the entity. The log records
    the user who initiated the request and the state of the entity at
    the time of the operation.
    """
    __tablename__ = "logs"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    request_method = Column(Enum(RequestMethod), index=True)
    request_url = Column(String(256), index=True)
    request_params = Column(JSON)
    entity_action = Column(Enum(EntityAction), index=True)
    entity_tablename = Column(String(128), index=True)
    entity_id = Column(BigInteger, index=True)
    entity_dict = Column(JSON)

    def __init__(self, current_user: User, request: Request,
                 entity: DeclarativeBase, entity_action: EntityAction):
        """
        Initializes a Log instance with details of the request, entity,
        and action performed. It sets the user ID, request method, URL,
        request parameters, and entity information, including the action
        performed and the entity state at the time of the request.
        """
        self.user_id = current_user.id if current_user else None
        self.request_method = request.method
        self.request_url = request.url.path
        self.request_params = self._to_dict(request.query_params._dict)
        self.entity_action = entity_action
        self.entity_tablename = entity.__tablename__
        self.entity_id = entity.id
        self.entity_dict = self._to_dict(entity.__dict__)

    def _to_dict(self, entity_dict: dict) -> json:
        """
        Converts a dictionary of entity attributes into a dictionary of
        string representations, obscuring sensitive information based on
        predefined keys. This method filters out private attributes and
        returns a clean, readable representation of the entity's state.
        """
        return {x: repr(entity_dict[x])
                if x not in OBSCURED_KEYS else OBSCURED_VALUE
                for x in entity_dict if not x.startswith("_")}


async def after_startup(
    entity_manager: EntityManager,
    cache_manager: CacheManager, request: None,
    current_user: None,
    entity: None
):
    """
    Handles post-startup actions, such as initializing or configuring
    components related to the entity manager and cache manager. This
    function is invoked after the application starts and does not
    process any specific user or entity information.
    """
    ...


async def after_user_register(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user registration event, capturing details about the
    new user and the request. Returns the registered user.
    """
    log = Log(current_user, request, user, EntityAction.insert)
    await entity_manager.insert(log)
    return user


async def after_user_login(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user login event, capturing details about the user
    and the request. Returns the logged-in user.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_token_retrieve(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a token retrieval event, capturing details about the user
    and the request. Returns the user associated with the token.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_token_invalidate(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a token invalidation event, capturing details about the user
    and the request. Returns the user associated with the invalidated
    token.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_user_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user selection event, capturing details about the user
    and the request. Returns the selected user.
    """
    log = Log(current_user, request, user, EntityAction.select)
    await entity_manager.insert(log)
    return user


async def after_user_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user update event, capturing details about the user and
    the request. Returns the updated user.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_role_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user role update event, capturing details about the user and
    the request. Returns the user whose role was updated.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_password_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a password update event, capturing details about the user and
    the request. Returns the user whose password was updated.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_userpic_upload(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user picture upload event, capturing details about the user
    and the request. Returns the user whose picture was uploaded.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_userpic_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    """
    Logs a user picture deletion event, capturing details about the user
    and the request. Returns the user whose picture was deleted.
    """
    log = Log(current_user, request, user, EntityAction.update)
    await entity_manager.insert(log)
    return user


async def after_users_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    users: List[Collection]
) -> List[Collection]:
    """
    Logs a user list retrieval event for each user in the list,
    capturing details about each user and the request. Returns the
    list of users.
    """
    for user in users:
        log = Log(current_user, request, user, EntityAction.select)
        await entity_manager.insert(log)
    return users


async def after_collection_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection insertion event, capturing details about the
    collection and the request. Returns the newly inserted collection.
    """
    log = Log(current_user, request, collection, EntityAction.insert)
    await entity_manager.insert(log)
    return collection


async def after_collection_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection selection event, capturing details about the
    collection and the request. Returns the selected collection.
    """
    log = Log(current_user, request, collection, EntityAction.select)
    await entity_manager.insert(log)
    return collection


async def after_collection_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection update event, capturing details about the
    collection and the request. Returns the updated collection.
    """
    log = Log(current_user, request, collection, EntityAction.update)
    await entity_manager.insert(log)
    return collection


async def after_collection_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Logs a collection deletion event, capturing details about the
    collection and the request. Returns the deleted collection.
    """
    log = Log(current_user, request, collection, EntityAction.delete)
    await entity_manager.insert(log)
    return collection


async def after_collections_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collections: List[Collection]
) -> List[Collection]:
    """
    Logs a collections list retrieval event for each collection in the
    list, capturing details about each collection and the request.
    Returns the list of collections.
    """
    for collection in collections:
        log = Log(current_user, request, collection, EntityAction.select)
        await entity_manager.insert(log)
    return collections


async def after_document_upload(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Logs a document upload event, capturing details about the document
    and the request. Returns the uploaded document.
    """
    log = Log(current_user, request, document, EntityAction.insert)
    await entity_manager.insert(log)
    return document


async def after_document_download(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Logs a document download event, capturing details about the document
    and the request. Returns the downloaded document.
    """
    log = Log(current_user, request, document, EntityAction.select)
    await entity_manager.insert(log)
    return document


async def after_document_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Logs a document selection event, capturing details about the
    document and the request. Returns the selected document.
    """
    log = Log(current_user, request, document, EntityAction.select)
    await entity_manager.insert(log)
    return document


async def after_comment_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment insertion event, capturing details about the comment
    and the request. Returns the inserted comment.
    """
    log = Log(current_user, request, comment, EntityAction.insert)
    await entity_manager.insert(log)
    return comment


async def after_comment_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment retrieval event, capturing details about the comment
    and the request. Returns the selected comment.
    """
    log = Log(current_user, request, comment, EntityAction.select)
    await entity_manager.insert(log)
    return comment


async def after_comment_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment update event, capturing details about the updated
    comment and the request. Returns the updated comment.
    """
    log = Log(current_user, request, comment, EntityAction.update)
    await entity_manager.insert(log)
    return comment


async def after_comment_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Logs a comment deletion event, capturing details about the deleted
    comment and the request. Returns the deleted comment.
    """
    log = Log(current_user, request, comment, EntityAction.delete)
    await entity_manager.insert(log)
    return comment


async def after_comments_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comments: List[Comment]
) -> List[Comment]:
    """
    Logs the retrieval of a list of comments, capturing details about
    each comment and the request. Returns the list of comments.
    """
    for comment in comments:
        log = Log(current_user, request, comment, EntityAction.select)
        await entity_manager.insert(log)
    return comments


async def after_download_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    download: Download
) -> Download:
    """
    Logs the selection of a download event, capturing details about the
    download and the request. Returns the download record.
    """
    log = Log(current_user, request, download, EntityAction.select)
    await entity_manager.insert(log)
    return download


async def after_downloads_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    downloads: List[Download]
) -> List[Download]:
    """
    Logs the retrieval of a list of downloads, capturing details about
    each download and the request. Returns the list of downloads.
    """
    for download in downloads:
        log = Log(current_user, request, download, EntityAction.select)
        await entity_manager.insert(log)
    return downloads


async def after_favorite_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs the addition of a new favorite, capturing details about the
    favorite and the request. Returns the newly added favorite.
    """
    log = Log(current_user, request, favorite, EntityAction.insert)
    await entity_manager.insert(log)
    return favorite


async def after_favorite_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs the retrieval of a favorite, capturing details about the
    favorite and the request. Returns the favorite.
    """
    log = Log(current_user, request, favorite, EntityAction.select)
    await entity_manager.insert(log)
    return favorite


async def after_favorite_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    """
    Logs the deletion of a favorite, capturing details about the
    favorite and the request. Returns the deleted favorite.
    """
    log = Log(current_user, request, favorite, EntityAction.delete)
    await entity_manager.insert(log)
    return favorite


async def after_favorites_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorites: List[Favorite]
) -> List[Favorite]:
    """
    Logs the retrieval of a list of favorites, capturing details about
    each favorite and the request. Returns the list of retrieved
    favorites.
    """
    for favorite in favorites:
        log = Log(current_user, request, favorite, EntityAction.select)
        await entity_manager.insert(log)
    return favorites
