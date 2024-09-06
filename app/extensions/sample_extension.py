from typing import List, Union
from fastapi import Request
from app.models.user_models import User
from app.models.collection_models import Collection
from app.models.document_models import Document
from app.models.revision_models import Revision
from app.models.comment_models import Comment
from app.models.download_models import Download
from app.models.favorite_models import Favorite
from app.models.option_models import Option
from app.managers.entity_manager import EntityManager
from app.managers.cache_manager import CacheManager


async def on_startup(
    entity_manager: EntityManager,
    cache_manager: CacheManager, request: None,
    current_user: None,
    entity: None
):
    """
    Handles post-startup actions, such as initializing or configuring
    components related to the entity manager and cache manager. This
    function is invoked after the application starts and does not
    return anything.
    """
    ...


async def on_schedule(
    entity_manager: EntityManager,
    cache_manager: CacheManager, request: None,
    current_user: None,
    entity: None
):
    ...


async def after_user_register(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_user_login(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_token_retrieve(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_token_invalidate(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_user_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_user_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_role_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_password_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_userpic_upload(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_userpic_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    user: User
) -> User:
    ...
    return user


async def after_users_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    users: List[Collection]
) -> List[Collection]:
    ...
    return users

# =============================================================================


async def before_collection_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic before a collection entity is created,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def after_collection_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic after a collection entity is created,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def after_collection_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic after a collection entity is retrieved,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def before_collection_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic before a collection entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def after_collection_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic after a collection entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def before_collection_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic before a collection entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def after_collection_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collection: Collection
) -> Collection:
    """
    Executes additional logic after a collection entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return collection


async def after_collections_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    collections: List[Collection]
) -> List[Collection]:
    """
    Executes additional logic after a list of collection entities is
    selected, such as event logging, updating the database, managing
    the cache, performing file or network operations, or other actions.
    It takes the list of entities as input, applies the required
    post-processing, and returns the list of possibly modified
    entities.
    """
    ...
    return collections


async def before_document_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic before a document entity is created,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def after_document_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic after a document entity is created,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def after_document_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic after a document entity is retrieved,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def before_document_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic before a document entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def after_document_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic after a document entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def before_document_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic before a document entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def after_document_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    document: Document
) -> Document:
    """
    Executes additional logic after a document entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return document


async def after_documents_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    documents: List[Document]
) -> List[Document]:
    """
    Executes additional logic after a list of document entities is
    selected, such as event logging, updating the database, managing
    the cache, performing file or network operations, or other actions.
    It takes the list of entities as input, applies the required
    post-processing, and returns the list of possibly modified
    entities.
    """
    ...
    return documents


async def after_favorite_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    ...
    return favorite


async def after_favorite_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    ...
    return favorite


async def after_favorite_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorite: Favorite
) -> Favorite:
    ...
    return favorite


async def after_favorites_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    favorites: List[Favorite]
) -> List[Favorite]:
    ...
    return favorites


async def after_revision_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    revision: Revision
) -> Revision:
    ...
    return revision


async def after_revision_download(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    revision: Revision
) -> Revision:
    ...
    return revision


async def after_revisions_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    revisions: List[Revision]
) -> List[Favorite]:
    ...
    return revisions


async def after_download_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    download: Download
) -> Download:
    ...
    return download


async def after_downloads_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    downloads: List[Download]
) -> List[Download]:
    ...
    return downloads


async def before_comment_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic before a comment entity is created,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def after_comment_insert(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic after a comment entity is created,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def after_comment_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic after a comment entity is retrieved,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def before_comment_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic before a comment entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def after_comment_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic after a comment entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def before_comment_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic before a comment entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def after_comment_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comment: Comment
) -> Comment:
    """
    Executes additional logic after a comment entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return comment


async def after_comment_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    comments: List[Comment]
) -> List[Comment]:
    """
    Executes additional logic after a list of comment entities is
    retrieved, such as event logging, updating the database, managing
    the cache, performing file or network operations, or other actions.
    It takes the list of entities as input, applies the required
    post-processing, and returns the list of possibly modified
    entities.
    """
    ...
    return comments


async def after_option_select(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    option: Option
) -> Option:
    """
    Executes additional logic after an option entity is retrieved,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return option


async def before_option_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    option: Option
) -> Option:
    """
    Executes additional logic before an option entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return option


async def after_option_update(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    option: Option
) -> Option:
    """
    Executes additional logic after an option entity is updated,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return option


async def before_option_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    option: Option = None
) -> Union[Option, None]:
    """
    Executes additional logic before an option entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required pre-processing, and
    returns the possibly modified entity.
    """
    ...
    return option


async def after_option_delete(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    option: Option = None
) -> Union[Option, None]:
    """
    Executes additional logic after an option entity is deleted,
    such as event logging, updating the database, managing the cache,
    performing file or network operations, or other actions. It takes
    the entity as input, applies the required post-processing, and
    returns the possibly modified entity.
    """
    ...
    return option


async def after_option_list(
    entity_manager: EntityManager,
    cache_manager: CacheManager,
    request: Request,
    current_user: User,
    options: List[Option]
) -> List[Option]:
    """
    Executes additional logic after a list of option entities is
    retrieved, such as event logging, updating the database, managing
    the cache, performing file or network operations, or other actions.
    It takes the list of entities as input, applies the required
    post-processing, and returns the list of possibly modified
    entities.
    """
    ...
    return options
