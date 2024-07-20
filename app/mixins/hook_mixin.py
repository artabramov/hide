from app.context import get_context
from app.hooks import H


class HookMixin:

    async def hook(self, hook: H, entity=None):
        ctx = get_context()
        if hook.value in ctx.hooks:
            hook_functions = ctx.hooks[hook.value]
            for func in hook_functions:
                entity = await func(
                    entity, entity_manager=self.entity_manager,
                    cache_manager=self.cache_manager)
        return entity
