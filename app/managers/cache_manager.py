
from typing import Type, Optional, Union
from sqlalchemy.ext.serializer import dumps, loads
from sqlalchemy.orm import DeclarativeBase
from redis import Redis
from app.decorators.timed_deco import timed
from app.config import get_config
from app.log import get_log

cfg = get_config()
log = get_log()


class CacheManager:
    """
    Manages caching operations for SQLAlchemy entities using Redis.

    Provides methods to set, get, delete, and delete all cache entries
    for SQLAlchemy entities. Uses Redis for storage and supports
    asynchronous operations.
    """

    def __init__(self, cache: Redis):
        """Initialize the CacheManager with a Redis cache instance."""
        self.cache = cache

    def _get_key(self, entity: Type[DeclarativeBase],
                 entity_id: Union[int, str]) -> str:
        """
        Create a cache key based on the table name and
        the entity id (or asterisk).
        """
        return "%s:%s" % (entity.__tablename__, entity_id)

    @timed
    async def set(self, entity: DeclarativeBase):
        """Set an entity in the cache."""
        key = self._get_key(entity, entity.id)
        await self.cache.set(key, dumps(entity), ex=cfg.REDIS_EXPIRE)

    @timed
    async def get(self, cls: Type[DeclarativeBase],
                  entity_id: int) -> Optional[DeclarativeBase]:
        """Retrieve an entity from the cache."""
        key = self._get_key(cls, entity_id)
        entity_bytes = await self.cache.get(key)
        return loads(entity_bytes) if entity_bytes else None

    @timed
    async def delete(self, entity: DeclarativeBase):
        """Delete an entity from the cache."""
        key = self._get_key(entity, entity.id)
        await self.cache.delete(key)

    @timed
    async def delete_all(self, cls: Type[DeclarativeBase]):
        """Delete all entities of a given class from the cache."""
        key_pattern = self._get_key(cls, "*")
        for key in await self.cache.keys(key_pattern):
            await self.cache.delete(key)
