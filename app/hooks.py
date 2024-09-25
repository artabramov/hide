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
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager
from app.models.user_model import User
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
    # system hooks
    ON_STARTUP = "on_startup"
    ON_TIME_RETRIEVE = "on_time_retrieve"
    ON_TELEMETRY_RETRIEVE = "on_telemetry_retrieve"
    ON_LOCK_CREATE = "on_lock_create"
    ON_LOCK_RETRIEVE = "on_lock_retrieve"
    ON_LOCK_DELETE = "on_lock_delete"
    ON_CUSTOM_EXECUTE = "on_custom_execute"

    # user hooks
    BEFORE_USER_REGISTER = "before_user_register"
    AFTER_USER_REGISTER = "after_user_register"
    AFTER_USER_LOGIN = "after_user_login"
    BEFORE_USER_LOGIN = "before_user_login"
    BEFORE_USER_DELETE = "before_user_delete"
    AFTER_USER_DELETE = "after_user_delete"
    BEFORE_TOKEN_SELECT = "before_token_select"
    AFTER_TOKEN_SELECT = "after_token_select"
    BEFORE_TOKEN_INVALIDATE = "before_token_invalidate"
    AFTER_TOKEN_INVALIDATE = "after_token_invalidate"
    BEFORE_MFA_SELECT = "before_mfa_select"
    AFTER_MFA_SELECT = "after_mfa_select"
    AFTER_USER_SELECT = "after_user_select"
    BEFORE_USER_UPDATE = "before_user_update"
    AFTER_USER_UPDATE = "after_user_update"
    BEFORE_ROLE_UPDATE = "before_role_update"
    AFTER_ROLE_UPDATE = "after_role_update"
    BEFORE_PASSWORD_UPDATE = "before_password_update"
    AFTER_PASSWORD_UPDATE = "after_password_update"
    BEFORE_USERPIC_UPLOAD = "before_userpic_upload"
    AFTER_USERPIC_UPLOAD = "after_userpic_upload"
    BEFORE_USERPIC_DELETE = "before_userpic_delete"
    AFTER_USERPIC_DELETE = "after_userpic_delete"
    AFTER_USER_LIST = "after_user_list"

    # collection hooks
    BEFORE_COLLECTION_INSERT = "before_collection_insert"
    AFTER_COLLECTION_INSERT = "after_collection_insert"
    AFTER_COLLECTION_SELECT = "after_collection_select"
    BEFORE_COLLECTION_DELETE = "before_collection_delete"
    AFTER_COLLECTION_DELETE = "after_collection_delete"
    BEFORE_COLLECTION_UPDATE = "before_collection_update"
    AFTER_COLLECTION_UPDATE = "after_collection_update"
    AFTER_COLLECTION_LIST = "after_collection_list"

    # document hooks
    BEFORE_DOCUMENT_UPLOAD = "before_document_upload"
    AFTER_DOCUMENT_UPLOAD = "after_document_upload"
    BEFORE_DOCUMENT_REPLACE = "before_document_replace"
    AFTER_DOCUMENT_REPLACE = "after_document_replace"
    AFTER_DOCUMENT_SELECT = "after_document_select"
    BEFORE_DOCUMENT_UPDATE = "before_document_update"
    AFTER_DOCUMENT_UPDATE = "after_document_update"
    BEFORE_DOCUMENT_DELETE = "before_document_delete"
    AFTER_DOCUMENT_DELETE = "after_document_delete"
    AFTER_DOCUMENT_LIST = "after_document_list"

    # comment hooks
    BEFORE_COMMENT_INSERT = "before_comment_insert"
    AFTER_COMMENT_INSERT = "after_comment_insert"
    AFTER_COMMENT_SELECT = "after_comment_select"
    BEFORE_COMMENT_UPDATE = "before_comment_update"
    AFTER_COMMENT_UPDATE = "after_comment_update"
    BEFORE_COMMENT_DELETE = "before_comment_delete"
    AFTER_COMMENT_DELETE = "after_comment_delete"
    AFTER_COMMENT_LIST = "after_comment_list"

    # upload hooks
    AFTER_UPLOAD_SELECT = "after_upload_select"
    BEFORE_UPLOAD_DOWNLOAD = "before_upload_download"
    AFTER_UPLOAD_DOWNLOAD = "after_upload_download"
    AFTER_UPLOAD_LIST = "after_upload_list"

    # download hooks
    AFTER_DOWNLOAD_SELECT = "after_download_select"
    AFTER_DOWNLOAD_LIST = "after_download_list"

    # favorite hooks
    BEFORE_FAVORITE_INSERT = "before_favorite_insert"
    AFTER_FAVORITE_INSERT = "after_favorite_insert"
    AFTER_FAVORITE_SELECT = "after_favorite_select"
    BEFORE_FAVORITE_DELETE = "before_favorite_delete"
    AFTER_FAVORITE_DELETE = "after_favorite_delete"
    AFTER_FAVORITE_LIST = "after_favorite_list"

    # Option hooks
    BEFORE_OPTION_INSERT = "before_option_insert"
    AFTER_OPTION_INSERT = "after_option_insert"
    AFTER_OPTION_SELECT = "after_option_select"
    BEFORE_OPTION_UPDATE = "before_option_update"
    AFTER_OPTION_UPDATE = "after_option_update"
    BEFORE_OPTION_DELETE = "before_option_delete"
    AFTER_OPTION_DELETE = "after_option_delete"
    AFTER_OPTION_LIST = "after_option_list"


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
                 current_user: User = None):
        """
        Initializes the Hook class with an entity manager,
        cache manager, request, and current user. The entity manager
        is created from the provided session, and the cache manager is
        created from the provided Redis instance. The current user is
        optional and can be used to provide context for the hook
        execution.
        """
        self.entity_manager = EntityManager(session)
        self.cache_manager = CacheManager(cache)
        self.current_user = current_user

    async def do(self, hook_action: H, *args, **kwargs):
        """
        Executes the specified hook action by calling the associated
        functions with the provided entity manager, cache manager,
        request, current user, and data. The hook functions are
        retrieved from the context based on the hook action value and
        are invoked sequentially.
        """
        if hook_action.value in ctx.hooks:
            hook_functions = ctx.hooks[hook_action.value]
            for func in hook_functions:
                await func(self.entity_manager, self.cache_manager,
                           self.current_user, *args, **kwargs)
