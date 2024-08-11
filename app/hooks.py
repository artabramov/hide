from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
import enum
from app.context import get_context
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_models import User
from typing import Any
from fastapi import Request
from sqlalchemy.orm import DeclarativeBase

ctx = get_context()


class H(enum.Enum):
    AFTER_STARTUP = "after_startup"

    AFTER_USER_REGISTER = "after_user_register"
    AFTER_USER_LOGIN = "after_user_login"
    AFTER_TOKEN_RETRIEVE = "after_token_retrieve"
    AFTER_TOKEN_INVALIDATE = "after_token_invalidate"
    AFTER_USER_SELECT = "after_user_select"
    AFTER_USERPIC_UPLOAD = "after_userpic_upload"
    AFTER_USERPIC_DELETE = "after_userpic_delete"

    AFTER_ALBUM_INSERT = "after_album_insert"
    AFTER_ALBUM_SELECT = "after_album_select"
    AFTER_ALBUM_UPDATE = "after_album_update"
    AFTER_ALBUM_DELETE = "after_album_delete"
    AFTER_ALBUMS_LIST = "after_albums_list"


class Hook:

    def __init__(self, session: AsyncSession, cache: Redis,
                 request: Request = None, current_user: User = None):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.request = request
        self.current_user = current_user

    async def execute(self, hook: H, entity: DeclarativeBase = None) -> Any:
        if hook.value in ctx.hooks:
            hook_functions = ctx.hooks[hook.value]
            for func in hook_functions:
                entity = await func(self.entity_manager, self.cache_manager,
                                    self.request, self.current_user, entity)
        return entity
