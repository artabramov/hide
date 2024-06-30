"""Cache manager."""

from sqlalchemy.ext.serializer import dumps, loads
from app.config import get_config
from app.decorators.timed_deco import timed

cfg = get_config()


class CacheManager:
    """Cache manager."""

    def __init__(self, cache):
        """Init cache manager."""
        self.cache = cache

    def _get_key(self, entity, entity_id: int | str) -> str:
        """Get key for entity."""
        return "%s:%s" % (entity.__tablename__, entity_id)

    @timed
    async def set(self, entity: object):
        """Set entity in cache."""
        key = self._get_key(entity, entity.id)
        await self.cache.set(key, dumps(entity), ex=cfg.REDIS_EXPIRE)

    @timed
    async def get(self, cls: object, entity_id: int) -> object:
        """Get entity from cache."""
        key = self._get_key(cls, entity_id)
        entity_bytes = await self.cache.get(key)
        return loads(entity_bytes) if entity_bytes else None

    @timed
    async def delete(self, entity: object):
        """Delete entity from cache."""
        key = self._get_key(entity, entity.id)
        await self.cache.delete(key)

    @timed
    async def delete_all(self, cls: object):
        """Delete all class entities from cache."""
        key_pattern = self._get_key(cls, "*")
        for key in await self.cache.keys(key_pattern):
            await self.cache.delete(key)
