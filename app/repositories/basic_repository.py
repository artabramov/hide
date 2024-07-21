from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager


class BasicRepository:

    def __init__(self, session: AsyncSession, cache: Redis):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
