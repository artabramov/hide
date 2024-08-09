import enum
import json
from time import time
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, Enum, JSON
from app.models.user_models import User
from app.models.album_models import Album
from app.database import Base, sessionmanager
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import DeclarativeBase


class ActivityAction(enum.Enum):
    INSERT = "insert"
    SELECT = "select"
    UPDATE = "update"
    DELETE = "delete"

    REGISTER = "register"


class EntityTablename(enum.Enum):
    USERS = User.__tablename__
    ALBUMS = Album.__tablename__


class Activity(Base):
    __tablename__ = "activities"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    user_id = Column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=True)
    entity_tablename = Column(
        Enum(EntityTablename), nullable=False, index=True)
    entity_id = Column(BigInteger, nullable=False, index=True)
    entity_dict = Column(JSON)
    activity_action = Column(Enum(ActivityAction), nullable=False, index=True)

    def __init__(
            self,
            entity: DeclarativeBase,
            activity_action: ActivityAction,
            current_user: User = None
    ):
        self.user_id = current_user.id if current_user else None
        self.entity_tablename = EntityTablename(entity.__tablename__)
        self.entity_id = entity.id
        self.entity_dict = self._to_dict(entity)
        self.activity_action = activity_action

    def _to_dict(self, entity: DeclarativeBase) -> json:
        return {x: repr(entity.__dict__[x]) for x in entity.__dict__}


async def after_startup(
        entity_manager: EntityManager,
        cache_manager: CacheManager,
        current_user: None,
        entity: None
):
    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def after_user_register(entity_manager: EntityManager,
                              cache_manager: CacheManager, current_user: User,
                              user: User) -> User:
    activity = Activity(user, ActivityAction.REGISTER, current_user)
    await entity_manager.insert(activity)
    return user


async def after_album_insert(entity_manager: EntityManager,
                             cache_manager: CacheManager, current_user: User,
                             album: Album) -> Album:
    activity = Activity(album, ActivityAction.INSERT, current_user)
    await entity_manager.insert(activity)
    return album


async def after_album_select(entity_manager: EntityManager,
                             cache_manager: CacheManager, current_user: User,
                             album: Album) -> Album:
    activity = Activity(album, ActivityAction.SELECT, current_user)
    await entity_manager.insert(activity)
    return album


async def after_album_update(entity_manager: EntityManager,
                             cache_manager: CacheManager, current_user: User,
                             album: Album) -> Album:
    activity = Activity(album, ActivityAction.UPDATE, current_user)
    await entity_manager.insert(activity)
    return album


async def after_album_delete(entity_manager: EntityManager,
                             cache_manager: CacheManager, current_user: User,
                             album: Album) -> Album:
    activity = Activity(album, ActivityAction.DELETE, current_user)
    await entity_manager.insert(activity)
    return album
