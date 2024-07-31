from app.models.user_models import User
from app.models.album_models import Album
from app.postgres import Base, sessionmanager
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSON
from time import time
import enum


class EntityAction(enum.Enum):
    INSERT = "insert"
    SELECT = "select"
    UPDATE = "update"
    DELETE = "delete"


class EntityTablename(enum.Enum):
    USERS = User.__tablename__
    ALBUMS = Album.__tablename__


class Revision(Base):
    __tablename__ = "revisions"

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True, default=lambda: int(time()))
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True,
                     nullable=True)
    entity_tablename = Column(Enum(EntityTablename), nullable=False, index=True)
    entity_id = Column(BigInteger, nullable=False, index=True)
    entity_action = Column(Enum(EntityAction), nullable=False, index=True)
    entity_data = Column(JSON)


async def after_startup(entity_manager, cache_manager, _=None):
    a = 1

    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return a


async def after_user_register(entity_manager, cache_manager, entity: User):
    entity.user_summary = "after user register"
    await entity_manager.update(entity, commit=True)
    await cache_manager.set(entity)
    return entity


async def after_album_insert(entity_manager, cache_manager, album: Album):
    album.album_summary = str(album.album_summary) + " hooked"
    return album


async def after_album_select(entity_manager, cache_manager, album: Album):
    album.album_summary = str(album.album_summary) + " hooked"
    return album


async def after_album_update(entity_manager, cache_manager, album: Album):
    return album
