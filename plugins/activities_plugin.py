import enum
import json
from time import time
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, Enum, JSON, String
from app.models.user_models import User
from app.models.album_models import Album
from app.database import Base
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import DeclarativeBase
from typing import List
from fastapi import Request


class RequestMethod(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class EntityTablename(enum.Enum):
    users = "users"
    albums = "albums"


class EntityOperation(enum.Enum):
    insert = "insert"
    select = "select"
    update = "update"
    delete = "delete"


class Activity(Base):
    __tablename__ = "activities"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)

    request_method = Column(Enum(RequestMethod), index=True)
    request_url = Column(String(255), index=True)
    query_params = Column(JSON)

    entity_operation = Column(Enum(EntityOperation), index=True)
    entity_tablename = Column(Enum(EntityTablename), index=True)
    entity_id = Column(BigInteger, index=True)
    entity_dict = Column(JSON)

    def __init__(self, request: Request, entity: DeclarativeBase,
                 entity_operation: EntityOperation, current_user: User = None):
        self.user_id = current_user.id if current_user else None

        self.request_method = request.method
        self.request_url = request.url.path
        self.query_params = self._to_dict(request.query_params._dict)

        self.entity_operation = entity_operation
        self.entity_tablename = EntityTablename(entity.__tablename__)
        self.entity_id = entity.id
        self.entity_dict = self._to_dict(entity.__dict__)

    def _to_dict(self, entity_dict: dict) -> json:
        return {x: repr(entity_dict[x]) for x in entity_dict}


async def after_startup(entity_manager: EntityManager,
                        cache_manager: CacheManager, request: None,
                        current_user: None, entity: None):
    pass


async def after_user_register(entity_manager: EntityManager,
                              cache_manager: CacheManager, current_user: User,
                              user: User) -> User:
    activity = Activity(user, EntityOperation.USER_REGISTER, current_user)
    await entity_manager.insert(activity)
    return user


async def after_album_insert(entity_manager: EntityManager,
                             cache_manager: CacheManager, request: Request,
                             current_user: User, album: Album) -> Album:
    activity = Activity(request, album, EntityOperation.insert, current_user)
    await entity_manager.insert(activity)
    return album


async def after_album_select(entity_manager: EntityManager,
                             cache_manager: CacheManager, request: Request,
                             current_user: User, album: Album) -> Album:
    activity = Activity(request, album, EntityOperation.select, current_user)
    await entity_manager.insert(activity)
    return album


async def after_album_update(entity_manager: EntityManager,
                             cache_manager: CacheManager, request: Request,
                             current_user: User, album: Album) -> Album:
    activity = Activity(request, album, EntityOperation.update, current_user)
    await entity_manager.insert(activity)
    return album


async def after_album_delete(entity_manager: EntityManager,
                             cache_manager: CacheManager, current_user: User,
                             album: Album) -> Album:
    activity = Activity(album, ActivityAction.DELETE, current_user)
    await entity_manager.insert(activity)
    return album


async def after_albums_list(entity_manager: EntityManager,
                            cache_manager: CacheManager, current_user: User,
                            albums: List[Album]) -> List[Album]:

    for album in albums:
        activity = Activity(album, ActivityAction.LIST, current_user)
        await entity_manager.insert(activity)

    return albums
