from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
from app.context import get_context
from app.hooks import H


class BasicRepository:

    def __init__(self, session: AsyncSession, cache: Redis):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.file_manager = FileManager

    async def execute_hook(self, hook: H, entity=None):
        ctx = get_context()
        if hook.value in ctx.hooks:
            hook_functions = ctx.hooks[hook.value]
            for func in hook_functions:
                entity = await func(
                    entity, entity_manager=self.entity_manager,
                    cache_manager=self.cache_manager,
                    file_manager=self.file_manager)
        return entity
