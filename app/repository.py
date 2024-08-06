from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager, ID
from app.managers.cache_manager import CacheManager
from sqlalchemy.orm import DeclarativeBase
from typing import List


class Repository:
    """Manages CRUD operations and caching for SQLAlchemy models."""

    def __init__(self, session: AsyncSession, cache: Redis, entity_class):
        """Initializes the repository."""
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.entity_class = entity_class

    async def exists(self, **kwargs) -> bool:
        """Checks if an entity exists with the given criteria."""
        return await self.entity_manager.exists(self.entity_class, **kwargs)

    async def insert(self, entity: DeclarativeBase, commit: bool = True):
        """Inserts an entity and optionally caches it."""
        await self.entity_manager.insert(entity, commit=commit)

        if self.entity_class._cacheable and commit:
            await self.cache_manager.set(entity)

    async def select(self, **kwargs) -> DeclarativeBase | None:
        """Retrieves an entity by id or other criteria."""
        entity_id, entity = kwargs.get(ID), None

        if self.entity_class._cacheable and entity_id:
            entity = await self.cache_manager.get(self.entity_class, entity_id)

        if not entity and entity_id:
            entity = await self.entity_manager.select(
                self.entity_class, entity_id)

        elif not entity and kwargs:
            entity = await self.entity_manager.select_by(
                self.entity_class, **kwargs)

        if self.entity_class._cacheable and entity:
            await self.cache_manager.set(entity)

        return entity

    async def update(self, entity: DeclarativeBase, commit: bool = True):
        """Updates an entity and manages its cache status."""
        await self.entity_manager.update(entity, commit=commit)

        if self.entity_class._cacheable:
            if commit:
                await self.cache_manager.set(entity)
            else:
                await self.cache_manager.delete(entity)

    async def delete(self, entity: DeclarativeBase, commit: bool = True):
        """Deletes an entity and manages its cache status."""
        await self.entity_manager.delete(entity, commit=commit)

        if self.entity_class._cacheable:
            await self.cache_manager.delete(entity)

    async def select_all(self, **kwargs) -> List[DeclarativeBase]:
        """Retrieves all entities matching the given criteria."""
        entities = await self.entity_manager.select_all(
            self.entity_class, **kwargs)

        if self.entity_class._cacheable:
            for entity in entities:
                await self.cache_manager.set(entity)

        return entities

    async def count_all(self, **kwargs) -> int:
        """Counts all entities matching the given criteria."""
        return await self.entity_manager.count_all(self.entity_class, **kwargs)

    async def sum_all(self, column_name: str, **kwargs) -> int:
        """Sums a column's values for entities matching the criteria."""
        return await self.entity_manager.sum_all(
            self.entity_class, column_name, **kwargs)

    async def commit(self):
        """Commits the current transaction."""
        await self.entity_manager.commit()

    async def rollback(self):
        """Rolls back the current transaction."""
        await self.entity_manager.rollback()
