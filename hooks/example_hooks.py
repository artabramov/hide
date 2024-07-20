async def before_user_register(user, entity_manager=None, cache_manager=None):
    user.user_summary = "before user register"
    return user


async def after_user_register(user, entity_manager=None, cache_manager=None):
    user.user_summary = "after user register"
    await entity_manager.update(user, commit=True)
    await cache_manager.set(user)
    return user
