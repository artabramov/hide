async def before_user_register(user, entity_manager=None, cache_manager=None,
                               file_manager=None):
    user.user_summary = "before user register "
    return user
