from app.models.user_models import User
from app.log import get_log

log = get_log()


async def on_start(entity_manager, cache_manager, entity=None):
    a = 1
    return a


async def on_tick(entity_manager, cache_manager, entity=None):
    log.debug("tick")
    b = 1
    return b


async def before_user_register(entity_manager, cache_manager, entity: User):
    entity.user_summary = "before user register"
    return entity


async def after_user_register(entity_manager, cache_manager, entity: User):
    entity.user_summary = "after user register"
    await entity_manager.update(entity, commit=True)
    await cache_manager.set(entity)
    return entity
