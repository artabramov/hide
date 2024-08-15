from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
import enum
from app.context import get_context
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_models import User
from typing import Any
from fastapi import Request

ctx = get_context()


class H(enum.Enum):
    AFTER_STARTUP = "after_startup"

    AFTER_USER_REGISTER = "after_user_register"
    AFTER_USER_LOGIN = "after_user_login"
    AFTER_TOKEN_RETRIEVE = "after_token_retrieve"
    AFTER_TOKEN_INVALIDATE = "after_token_invalidate"
    AFTER_USER_SELECT = "after_user_select"
    AFTER_USER_UPDATE = "after_user_update"
    AFTER_ROLE_UPDATE = "after_role_update"
    AFTER_PASSWORD_UPDATE = "after_password_update"
    AFTER_USERPIC_UPLOAD = "after_userpic_upload"
    AFTER_USERPIC_DELETE = "after_userpic_delete"
    AFTER_USERS_LIST = "after_users_list"

    AFTER_COLLECTION_INSERT = "after_collection_insert"
    AFTER_COLLECTION_SELECT = "after_collection_select"
    AFTER_COLLECTION_UPDATE = "after_collection_update"
    AFTER_COLLECTION_DELETE = "after_collection_delete"
    AFTER_COLLECTIONS_LIST = "after_collections_list"

    AFTER_DOCUMENT_INSERT = "after_document_insert"
    AFTER_DOCUMENT_DOWNLOAD = "after_document_download"


class Hook:

    def __init__(self, session: AsyncSession, cache: Redis,
                 request: Request = None, current_user: User = None):
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.request = request
        self.current_user = current_user

    async def execute(self, hook_action: H, data: Any = None) -> Any:
        if hook_action.value in ctx.hooks:
            hook_functions = ctx.hooks[hook_action.value]
            for func in hook_functions:
                data = await func(self.entity_manager, self.cache_manager,
                                  self.request, self.current_user, data)
        return data
