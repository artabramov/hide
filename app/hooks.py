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


class HookAction(enum.Enum):
    after_startup = "after_startup"

    after_user_register = "after_user_register"
    after_user_login = "after_user_login"
    after_token_retrieve = "after_token_retrieve"
    after_token_invalidate = "after_token_invalidate"
    after_user_select = "after_user_select"
    after_user_update = "after_user_update"
    after_role_update = "after_role_update"
    after_password_update = "after_password_update"
    after_userpic_upload = "after_userpic_upload"
    after_userpic_delete = "after_userpic_delete"
    after_users_list = "after_users_list"

    after_collection_insert = "after_collection_insert"
    after_collection_select = "after_collection_select"
    after_collection_update = "after_collection_update"
    after_collection_delete = "after_collection_delete"
    after_collections_list = "after_collections_list"


class Hook:

    def __init__(self, session: AsyncSession, cache: Redis,
                 request: Request = None, current_user: User = None):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.request = request
        self.current_user = current_user

    async def execute(self, hook_action: HookAction,
                      entity: DeclarativeBase = None) -> Any:
        if hook_action.value in ctx.hooks:
            hook_functions = ctx.hooks[hook_action.value]
            for func in hook_functions:
                entity = await func(self.entity_manager, self.cache_manager,
                                    self.request, self.current_user, entity)
        return entity
