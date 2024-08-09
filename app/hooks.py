from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
import enum
from app.context import get_context
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_models import User
from typing import Any

ctx = get_context()


class H(enum.Enum):
    AFTER_STARTUP = "after_startup"
    AFTER_USER_REGISTER = "after_user_register"
    AFTER_ALBUM_INSERT = "after_album_insert"
    AFTER_ALBUM_SELECT = "after_album_select"
    AFTER_ALBUM_UPDATE = "after_album_update"


class Hook:

    def __init__(self, session: AsyncSession, cache: Redis,
                 current_user: User = None):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.current_user = current_user

    async def execute(self, hook: H, entity=None) -> Any:
        if hook.value in ctx.hooks:
            hook_functions = ctx.hooks[hook.value]
            for func in hook_functions:
                entity = await func(self.entity_manager, self.cache_manager,
                                    self.current_user, entity)
        return entity
