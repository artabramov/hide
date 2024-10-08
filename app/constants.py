# Error location is the request headers.
LOC_HEADER = "header"

# Error location is the cookie values.
LOC_COOKIE = "cookie"

# Error location is the URL path.
LOC_PATH = "path"

# Error location is the query parameters.
LOC_QUERY = "query"

# Error location is the request body.
LOC_BODY = "body"

# The token is missing from the request headers (403).
ERR_VALUE_REQUIRED = "token_missing"

# The token has expired and is no longer valid (403).
ERR_TOKEN_EXPIRED = "token_expired"

# The token is invalid and cannot be processed (403).
ERR_TOKEN_INVALID = "token_invalid"

# The token contains an invalid token identifier (403).
ERR_TOKEN_REJECTED = "token_rejected"

# The user is deleted or could not be found (403).
ERR_TOKEN_ORPHANED = "token_orphaned"

# The user is inactive and cannot access the resource (403).
ERR_USER_INACTIVE = "user_inactive"

# The user is temporarily suspended; try again later (403).
ERR_USER_SUSPENDED = "user_suspended"

# The user role is insufficient for this action (403).
ERR_USER_REJECTED = "user_rejected"

# The user cannot perform this action on the resource (403).
ERR_RESOURCE_FORBIDDEN = "resource_forbidden"

# The requested resource could not be found (404).
ERR_RESOURCE_NOT_FOUND = "resource_not_found"

# The resource that is being accessed is locked (423).
ERR_RESOURCE_LOCKED = "resource_locked"

# The value provided is empty (422).
ERR_VALUE_EMPTY = "value_empty"

# The value provided is invalid (422).
ERR_VALUE_INVALID = "value_invalid"

# The value provided already exists (422).
ERR_VALUE_DUPLICATED = "value_duplicated"

# The file MIME type is not supported for the operation (422).
ERR_MIMETYPE_UNSUPPORTED = "mimetype_unsupported"

# Internal server error (500).
ERR_SERVER_ERROR = "Internal server error"

# Hook types used to manage various pre-event and post-event actions
# within the app. These hooks are used to trigger corresponding funcs
# that handle tasks related to app, users management, collections,
# datafiles, comments, revisions, favorites, etc.

# service hooks
HOOK_ON_TIME_RETRIEVE = "on_time_retrieve"
HOOK_ON_TELEMETRY_RETRIEVE = "on_telemetry_retrieve"
HOOK_ON_LOCK_CREATE = "on_lock_create"
HOOK_ON_LOCK_RETRIEVE = "on_lock_retrieve"
HOOK_ON_LOCK_DELETE = "on_lock_delete"
HOOK_ON_CACHE_ERASE = "on_cache_erase"
HOOK_ON_CUSTOM_EXECUTE = "on_custom_execute"

# user hooks
HOOK_BEFORE_USER_REGISTER = "before_user_register"
HOOK_AFTER_USER_REGISTER = "after_user_register"
HOOK_BEFORE_USER_LOGIN = "before_user_login"
HOOK_AFTER_USER_LOGIN = "after_user_login"
HOOK_BEFORE_USER_DELETE = "before_user_delete"
HOOK_AFTER_USER_DELETE = "after_user_delete"
HOOK_BEFORE_TOKEN_RETRIEVE = "before_token_retrieve"
HOOK_AFTER_TOKEN_RETRIEVE = "after_token_retrieve"
HOOK_BEFORE_TOKEN_INVALIDATE = "before_token_invalidate"
HOOK_AFTER_TOKEN_INVALIDATE = "after_token_invalidate"
HOOK_BEFORE_MFA_SELECT = "before_mfa_select"
HOOK_AFTER_MFA_SELECT = "after_mfa_select"
HOOK_AFTER_USER_SELECT = "after_user_select"
HOOK_BEFORE_USER_UPDATE = "before_user_update"
HOOK_AFTER_USER_UPDATE = "after_user_update"
HOOK_BEFORE_ROLE_CHANGE = "before_role_change"
HOOK_AFTER_ROLE_CHANGE = "after_role_change"
HOOK_BEFORE_PASSWORD_CHANGE = "before_password_change"
HOOK_AFTER_PASSWORD_CHANGE = "after_password_change"
HOOK_BEFORE_USERPIC_UPLOAD = "before_userpic_upload"
HOOK_AFTER_USERPIC_UPLOAD = "after_userpic_upload"
HOOK_BEFORE_USERPIC_DELETE = "before_userpic_delete"
HOOK_AFTER_USERPIC_DELETE = "after_userpic_delete"
HOOK_AFTER_USER_LIST = "after_user_list"

# collection hooks
HOOK_BEFORE_COLLECTION_INSERT = "before_collection_insert"
HOOK_AFTER_COLLECTION_INSERT = "after_collection_insert"
HOOK_AFTER_COLLECTION_SELECT = "after_collection_select"
HOOK_BEFORE_COLLECTION_UPDATE = "before_collection_update"
HOOK_AFTER_COLLECTION_UPDATE = "after_collection_update"
HOOK_BEFORE_COLLECTION_DELETE = "before_collection_delete"
HOOK_AFTER_COLLECTION_DELETE = "after_collection_delete"
HOOK_AFTER_COLLECTION_LIST = "after_collection_list"

# datafile hooks
HOOK_BEFORE_DATAFILE_UPLOAD = "before_datafile_upload"
HOOK_AFTER_DATAFILE_UPLOAD = "after_datafile_upload"
HOOK_BEFORE_DATAFILE_REPLACE = "before_datafile_replace"
HOOK_AFTER_DATAFILE_REPLACE = "after_datafile_replace"
HOOK_AFTER_DATAFILE_SELECT = "after_datafile_select"
HOOK_BEFORE_DATAFILE_UPDATE = "before_datafile_update"
HOOK_AFTER_DATAFILE_UPDATE = "after_datafile_update"
HOOK_BEFORE_DATAFILE_DELETE = "before_datafile_delete"
HOOK_AFTER_DATAFILE_DELETE = "after_datafile_delete"
HOOK_AFTER_DATAFILE_LIST = "after_datafile_list"

# comment hooks
HOOK_BEFORE_COMMENT_INSERT = "before_comment_insert"
HOOK_AFTER_COMMENT_INSERT = "after_comment_insert"
HOOK_AFTER_COMMENT_SELECT = "after_comment_select"
HOOK_BEFORE_COMMENT_UPDATE = "before_comment_update"
HOOK_AFTER_COMMENT_UPDATE = "after_comment_update"
HOOK_BEFORE_COMMENT_DELETE = "before_comment_delete"
HOOK_AFTER_COMMENT_DELETE = "after_comment_delete"
HOOK_AFTER_COMMENT_LIST = "after_comment_list"

# revision hooks
HOOK_AFTER_REVISION_SELECT = "after_revision_select"
HOOK_BEFORE_REVISION_DOWNLOAD = "before_revision_download"
HOOK_AFTER_REVISION_DOWNLOAD = "after_revision_download"
HOOK_AFTER_REVISION_LIST = "after_revision_list"

# download hooks
HOOK_AFTER_DOWNLOAD_SELECT = "after_download_select"
HOOK_AFTER_DOWNLOAD_LIST = "after_download_list"

# favorite hooks
HOOK_BEFORE_FAVORITE_INSERT = "before_favorite_insert"
HOOK_AFTER_FAVORITE_INSERT = "after_favorite_insert"
HOOK_AFTER_FAVORITE_SELECT = "after_favorite_select"
HOOK_BEFORE_FAVORITE_DELETE = "before_favorite_delete"
HOOK_AFTER_FAVORITE_DELETE = "after_favorite_delete"
HOOK_AFTER_FAVORITE_LIST = "after_favorite_list"

# Option hooks
HOOK_BEFORE_OPTION_INSERT = "before_option_insert"
HOOK_AFTER_OPTION_INSERT = "after_option_insert"
HOOK_AFTER_OPTION_SELECT = "after_option_select"
HOOK_BEFORE_OPTION_UPDATE = "before_option_update"
HOOK_AFTER_OPTION_UPDATE = "after_option_update"
HOOK_BEFORE_OPTION_DELETE = "before_option_delete"
HOOK_AFTER_OPTION_DELETE = "after_option_delete"
HOOK_AFTER_OPTION_LIST = "after_option_list"
