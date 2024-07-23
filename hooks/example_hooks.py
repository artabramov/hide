from app.models.user_models import User


async def on_startup(entity_manager, cache_manager, entity=None):
    a = 1
    return a


async def before_user_register(entity_manager, cache_manager, entity: User):
    entity.user_summary = "before user register"
    return entity


async def after_user_register(entity_manager, cache_manager, entity: User):
    entity.user_summary = "after user register"
    await entity_manager.update(entity, commit=True)
    await cache_manager.set(entity)
    return entity
