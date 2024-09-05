"""
This module defines a system for executing various hooks based on
specific actions within the application. It includes the Hook class,
which orchestrates post-event operations by interacting with
EntityManager and CacheManager. The H enumeration specifies different
hook types, and the Hook class manages their execution, handling actions
related to user management, collections, documents, comments, downloads,
and favorites. This setup enables asynchronous processing and integrates
seamlessly with session and caching systems to ensure efficient state
management and responsiveness to application events.
"""

import enum
from typing import Any
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_models import User
from app.context import get_context

ctx = get_context()


class H(enum.Enum):
    """
    Defines an enumeration of hook types used to manage various
    post-event operations within the application. Each item of this
    enumeration represents a specific action or event, such as user
    registration, document upload, or comment update. These hook types
    are used to trigger corresponding functions that handle tasks
    related to user management, collections, documents, comments,
    downloads, and favorites.
    """
    ON_STARTUP = "on_startup"
    ON_SCHEDULE = "on_schedule"

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

    # =========================================================================

    # Collection hooks
    BEFORE_COLLECTION_INSERT = "before_collection_insert"
    BEFORE_COLLECTION_UPDATE = "before_collection_update"
    BEFORE_COLLECTION_DELETE = "before_collection_delete"
    AFTER_COLLECTION_INSERT = "after_collection_insert"
    AFTER_COLLECTION_SELECT = "after_collection_select"
    AFTER_COLLECTION_UPDATE = "after_collection_update"
    AFTER_COLLECTION_DELETE = "after_collection_delete"
    AFTER_COLLECTIONS_LIST = "after_collections_list"

    # Document hooks
    BEFORE_DOCUMENT_INSERT = "before_document_insert"
    BEFORE_DOCUMENT_UPDATE = "before_document_update"
    BEFORE_DOCUMENT_DELETE = "before_document_delete"
    AFTER_DOCUMENT_INSERT = "after_document_insert"
    AFTER_DOCUMENT_SELECT = "after_document_select"
    AFTER_DOCUMENT_UPDATE = "after_document_update"
    AFTER_DOCUMENT_DELETE = "after_document_delete"
    AFTER_DOCUMENTS_LIST = "after_documents_list"

    AFTER_FAVORITE_INSERT = "after_favorite_insert"
    AFTER_FAVORITE_SELECT = "after_favorite_select"
    AFTER_FAVORITE_DELETE = "after_favorite_delete"
    AFTER_FAVORITES_LIST = "after_favorites_list"

    AFTER_REVISION_SELECT = "after_revision_select"
    AFTER_REVISION_DOWNLOAD = "after_revision_download"
    AFTER_REVISIONS_LIST = "after_revisions_list"

    AFTER_DOWNLOAD_SELECT = "after_download_select"
    AFTER_DOWNLOADS_LIST = "after_downloads_list"

    AFTER_COMMENT_INSERT = "after_comment_insert"
    AFTER_COMMENT_SELECT = "after_comment_select"
    AFTER_COMMENT_UPDATE = "after_comment_update"
    AFTER_COMMENT_DELETE = "after_comment_delete"
    AFTER_COMMENTS_LIST = "after_comments_list"


class Hook:
    """
    Manages and executes various hooks for handling post-event
    operations within the application. This class initializes with
    necessary components such as an entity manager, cache manager,
    request, and current user. The execute method runs the appropriate
    hook functions based on the specified hook action, processing data
    as required and returning the result.
    """

    def __init__(self, session: AsyncSession, cache: Redis,
                 request: Request = None, current_user: User = None):
        """
        Initializes the Hook class with an entity manager,
        cache manager, request, and current user. The entity manager
        is created from the provided session, and the cache manager is
        created from the provided Redis instance. The request and
        current user are optional and can be used to provide context
        for the hook execution.
        """
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.request = request
        self.current_user = current_user

    async def execute(self, hook_action: H, data: Any = None) -> Any:
        """
        Executes the specified hook action by calling the associated
        functions with the provided entity manager, cache manager,
        request, current user, and data. The hook functions are
        retrieved from the context based on the hook action value and
        are invoked sequentially. Returns the processed data after
        executing all hook functions.
        """
        if hook_action.value in ctx.hooks:
            hook_functions = ctx.hooks[hook_action.value]
            for func in hook_functions:
                data = await func(self.entity_manager, self.cache_manager,
                                  self.request, self.current_user, data)
        return data
