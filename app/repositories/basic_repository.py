from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from abc import ABC, abstractmethod


class BasicRepository(ABC):

    def __init__(self, session: AsyncSession, cache: Redis):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)

    @abstractmethod
    async def exists(self):
        ...

    @abstractmethod
    async def insert(self):
        ...

    @abstractmethod
    async def select(self):
        ...

    @abstractmethod
    async def update(self):
        ...

    @abstractmethod
    async def delete(self):
        ...

    @abstractmethod
    async def select_all(self):
        ...

    @abstractmethod
    async def count_all(self):
        ...

    async def commit(self):
        await self.entity_manager.commit()

    async def rollback(self):
        await self.entity_manager.rollback()
