from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from abc import ABC, abstractmethod


class BasicRepository(ABC):

    def __init__(self, session: AsyncSession, cache: Redis, entity_class):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.entity_class = entity_class

    async def exists(self, **kwargs) -> bool:
        return await self.entity_manager.exists(self.entity_class, **kwargs)

    async def select_all(self, **kwargs) -> list:
        entities = await self.entity_manager.select_all(
            self.entity_class, **kwargs)

        for entity in entities:
            await self.cache_manager.set(entity)

        return entities

    async def count_all(self, **kwargs) -> int:
        return await self.entity_manager.count_all(self.entity_class, **kwargs)

    async def sum_all(self, column_name: str, **kwargs) -> int:
        return await self.entity_manager.sum_all(
            self.entity_class, column_name, **kwargs)

    async def commit(self):
        await self.entity_manager.commit()

    async def rollback(self):
        await self.entity_manager.rollback()

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
