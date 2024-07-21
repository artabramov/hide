from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
import enum
from app.context import get_context

ctx = get_context()


class H(enum.Enum):
    ON_EXECUTE = "on_execute"
    BEFORE_USER_REGISTER = "before_user_register"
    AFTER_USER_REGISTER = "after_user_register"


class Hook:

    def __init__(self, entity_manager: EntityManager,
                 cache_manager: CacheManager):
        self.entity_manager = entity_manager
        self.cache_manager = cache_manager

    async def execute(self, hook: H, entity=None):
        if hook.value in ctx.hooks:
            hook_functions = ctx.hooks[hook.value]
            for func in hook_functions:
                entity = await func(
                    entity_manager=self.entity_manager,
                    cache_manager=self.cache_manager,
                    entity=entity)
        return entity
